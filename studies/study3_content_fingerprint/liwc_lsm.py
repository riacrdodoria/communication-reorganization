"""Language Style Matching (LSM) computed with the BP-LIWC2015 dictionary.
LSM (Ireland & Pennebaker 2010) on the 9 function-word categories; also computes LIWC affect (posemo/
negemo) and cognitive-process proportions per window. Each is cross-referenced with the reorganization
metrics. NOTE: the BP-LIWC2015 dictionary is licensed (Carvalho et al. 2024) and is NOT redistributed
with this repository; set the LIWC_DIC environment variable to a local copy. Outputs hold only numeric
per-window scores (no dictionary content)."""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
from collections import Counter
DIC=os.environ.get("LIWC_DIC","BP-LIWC2015.dic")
GM=Path("data/metrics_gorman_l8"); TXT=Path("data/text_startup"); WIN=90
WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return WORD.findall(str(s).lower())

# ---- parse LIWC .dic ----
def load_liwc(path):
    lines=open(path,encoding="utf-8-sig").read().splitlines()
    pct=[i for i,l in enumerate(lines) if l.strip()=="%"]
    h0,h1=pct[0],pct[1]
    exact={}; wild=[]   # wild: list of (stem, frozenset(cats))
    for l in lines[h1+1:]:
        if not l.strip(): continue
        parts=l.split("\t")
        term=parts[0].strip().lower()
        cats=set()
        for x in parts[1:]:
            x=x.strip()
            if x.isdigit(): cats.add(int(x))
        if not term or not cats: continue
        if term.endswith("*"): wild.append((term[:-1],frozenset(cats)))
        else: exact[term]=exact.get(term,set())|cats
    # index wildcards by stem for prefix lookup
    wildset={}
    for stem,cats in wild:
        wildset.setdefault(stem,set()).update(cats)
    return exact,wildset
EXACT,WILD=load_liwc(DIC)
def token_cats(tok):
    cats=set(EXACT.get(tok,()))
    for k in range(1,len(tok)+1):
        c=WILD.get(tok[:k])
        if c: cats|=c
    return cats
LSM_CATS={3:"ppron",9:"ipron",10:"article",11:"prep",12:"auxverb",13:"adverb",14:"conj",15:"negate",25:"quant"}
def cat_props(tokens):
    n=len(tokens)
    if n==0: return None
    cnt=Counter()
    for t in tokens:
        for c in token_cats(t): cnt[c]+=1
    return {c:cnt[c]/n for c in cnt}, n
def lsm_pair(ta,tb):
    pa=cat_props(ta); pb=cat_props(tb)
    if pa is None or pb is None: return np.nan
    pa,pb=pa[0],pb[0]; vals=[]
    for c in LSM_CATS:
        a=pa.get(c,0.0); b=pb.get(c,0.0)
        if a+b>0: vals.append(1-abs(a-b)/(a+b))
        else: vals.append(1.0)   # both zero = perfect match on that category
    return float(np.mean(vals))

rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]).reset_index(drop=True)
    df["tok"]=df["text"].apply(toks)
    df["bin"]=(df["onset"]//WIN*WIN).astype(int)
    # pairwise LSM (consecutive turns) + per-utterance affect/cog proportions
    lsm=np.full(len(df),np.nan); pos=np.full(len(df),np.nan); neg=np.full(len(df),np.nan); cog=np.full(len(df),np.nan)
    for i in range(len(df)):
        cp=cat_props(df["tok"][i])
        if cp is not None:
            p=cp[0]; pos[i]=p.get(31,0.0); neg[i]=p.get(32,0.0); cog[i]=p.get(50,0.0)
        if i>0: lsm[i]=lsm_pair(df["tok"][i-1],df["tok"][i])
    df["lsm"]=lsm; df["pos"]=pos; df["neg"]=neg; df["cog"]=cog
    g=pd.read_csv(gp); g["bin"]=(g["second"]//WIN*WIN).astype(int)
    gagg=g.groupby("bin")[["entropy_g","det_g","rmse_g"]].mean()
    for b,sub in df.groupby("bin"):
        if b not in gagg.index or len(sub)<3: continue
        rows.append(dict(mid=mid,bin=int(b),
            entropy_g=gagg.loc[b,"entropy_g"],det_g=gagg.loc[b,"det_g"],rmse_g=gagg.loc[b,"rmse_g"],
            liwc_lsm=np.nanmean(sub["lsm"]),liwc_posemo=np.nanmean(sub["pos"]),
            liwc_negemo=np.nanmean(sub["neg"]),liwc_cogproc=np.nanmean(sub["cog"])))
out=pd.DataFrame(rows); out.to_csv("liwc_lsm_windows.csv",index=False)
print(f"BP-LIWC2015 loaded: {len(EXACT)} exact + {len(WILD)} wildcard stems.  windows={len(out)}\n")

NP=500; rng=np.random.default_rng(0)
def z(a): a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stf(feat,metric):
    zs=[]
    for mid,gg in out.groupby("mid"):
        gg=gg.dropna(subset=[feat,metric]); n=len(gg)
        if n<8: continue
        zx=z(gg[feat].to_numpy(float)); zy=z(gg[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n; sh=rng.integers(2,n-2,size=NP); ix=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[ix]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
st=lambda z:'***' if abs(z)>3.29 else '**' if abs(z)>2.58 else '*' if abs(z)>1.96 else ''
print(f"{'measure (BP-LIWC2015)':24}|{'ENTROPY':>9}|{'%DET':>9}|{'RMSE':>9}")
for f,lab in [("liwc_lsm","LSM (9 funct cats)"),("liwc_posemo","posemo"),("liwc_negemo","negemo"),("liwc_cogproc","cogproc")]:
    ze,zd,zr=stf(f,'entropy_g'),stf(f,'det_g'),stf(f,'rmse_g')
    print(f"{lab:24}|{ze:>+6.2f}{st(ze):<3}|{zd:>+6.2f}{st(zd):<3}|{zr:>+6.2f}{st(zr):<3}")
# agreement with curated-list LSM (triangulation_windows.csv) if present
if Path("triangulation_windows.csv").exists():
    t=pd.read_csv("triangulation_windows.csv")[["mid","bin","lsm"]].rename(columns={"lsm":"lsm_curated"})
    m=out.merge(t,on=["mid","bin"]).dropna(subset=["liwc_lsm","lsm_curated"])
    from scipy.stats import pearsonr
    print(f"\nAgreement BP-LIWC2015 LSM vs curated-list LSM (window level): r={pearsonr(m.liwc_lsm,m.lsm_curated)[0]:+.3f} (n={len(m)})")
