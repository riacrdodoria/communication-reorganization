"""LIWC psychological-category map of reorganization (BP-LIWC2015).
For each category: window-level proportion (pooled hits/tokens), cross-referenced with entropy_g/det_g/
rmse_g (Stouffer, within-meeting circular null) BOTH raw AND controlling for turn length (partial) —
because the LSM analysis showed that sparse-proportion lexical measures can become turn-length proxies.
Only categories surviving the turn-length control are retained. BH-FDR across categories. NOTE: the
BP-LIWC2015 dictionary is licensed (Carvalho et al. 2024) and is NOT redistributed here; set LIWC_DIC to
a local copy. Outputs are numeric only (no dictionary content)."""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
from collections import Counter
DIC=os.environ.get("LIWC_DIC","BP-LIWC2015.dic")
GM=Path("data/metrics_gorman_l8"); TXT=Path("data/text_startup"); WIN=90
WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return WORD.findall(str(s).lower())
def load_liwc(path):
    lines=open(path,encoding="utf-8-sig").read().splitlines()
    pct=[i for i,l in enumerate(lines) if l.strip()=="%"]
    exact={}; wild={}
    for l in lines[pct[1]+1:]:
        if not l.strip(): continue
        p=l.split("\t"); term=p[0].strip().lower()
        cats={int(x) for x in p[1:] if x.strip().isdigit()}
        if not term or not cats: continue
        if term.endswith("*"): wild.setdefault(term[:-1],set()).update(cats)
        else: exact.setdefault(term,set()).update(cats)
    return exact,wild
EXACT,WILD=load_liwc(DIC)
def token_cats(t):
    c=set(EXACT.get(t,()))
    for k in range(1,len(t)+1):
        w=WILD.get(t[:k])
        if w: c|=w
    return c
# categories to report (num:label), grouped
CATS={83:"power",82:"achievement",81:"affiliation",84:"reward",85:"risk",
51:"insight",52:"cause",53:"discrep",54:"tentative",55:"certainty",56:"differ",50:"cogproc(all)",
31:"posemo",32:"negemo",40:"social",4:"pron_I",5:"pron_we",6:"pron_you",
23:"interrog",123:"assent",124:"nonfluency",125:"filler",
90:"focuspast",91:"focuspresent",92:"focusfuture"}
TARGET=set(CATS)

rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]).reset_index(drop=True)
    df["tok"]=df["text"].apply(toks); df["nw"]=df["tok"].apply(len).clip(lower=1)
    df["bin"]=(df["onset"]//WIN*WIN).astype(int)
    g=pd.read_csv(gp); g["bin"]=(g["second"]//WIN*WIN).astype(int)
    gagg=g.groupby("bin")[["entropy_g","det_g","rmse_g"]].mean()
    for b,sub in df.groupby("bin"):
        if b not in gagg.index or len(sub)<3: continue
        cnt=Counter(); ntok=0
        for tl in sub["tok"]:
            ntok+=len(tl)
            for t in tl:
                for c in token_cats(t)&TARGET: cnt[c]+=1
        if ntok==0: continue
        r=dict(mid=mid,bin=int(b),entropy_g=gagg.loc[b,"entropy_g"],det_g=gagg.loc[b,"det_g"],
            rmse_g=gagg.loc[b,"rmse_g"],turn_len=sub["nw"].mean())
        for c,lab in CATS.items(): r[lab]=cnt[c]/ntok
        rows.append(r)
out=pd.DataFrame(rows); out.to_csv("liwc_map_windows.csv",index=False)
print(f"BP-LIWC2015 map: {len(out)} windows, {len(CATS)} categories\n")

NP=500; rng=np.random.default_rng(0)
def z(a): a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stf(feat,metric,ctrl=None):
    zs=[]
    for mid,gg in out.groupby("mid"):
        cols=[feat,metric]+([ctrl] if ctrl else []); gg=gg.dropna(subset=cols); n=len(gg)
        if n<10: continue
        zx=z(gg[feat].to_numpy(float)); zy=z(gg[metric].to_numpy(float))
        if zx is None or zy is None: continue
        if ctrl:
            zc=z(gg[ctrl].to_numpy(float))
            if zc is None: continue
            zx=zx-(zx@zc/(zc@zc))*zc; zy=zy-(zy@zc/(zc@zc))*zc
        obs=float(zx@zy)/n; sh=rng.integers(2,n-2,size=NP); ix=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[ix]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
from scipy.stats import norm
# rank by det_g raw, show raw + turn-length-controlled
res=[]
for lab in CATS.values():
    zr=stf(lab,"det_g"); zp=stf(lab,"det_g","turn_len")
    res.append(dict(cat=lab,z_det_raw=zr,z_det_ctrl=zp))
R=pd.DataFrame(res)
R["q_raw"]=bh(2*norm.sf(np.abs(R.z_det_raw)))
R["q_ctrl"]=bh(2*norm.sf(np.abs(R.z_det_ctrl)))
R=R.sort_values("z_det_ctrl")
star=lambda q:'***' if q<.001 else '**' if q<.01 else '*' if q<.05 else 'ns'
print(f"{'category':16}| {'Z vs %DET (raw)':>16} | {'Z vs %DET | turnlen':>20} | survives?")
print("-"*72)
for _,r in R.iterrows():
    surv = "YES" if r.q_ctrl<.05 else "no (turn-len artifact)" if r.q_raw<.05 else "—"
    print(f"{r['cat']:16}| {r.z_det_raw:>+7.2f} {star(r.q_raw):<4}      | {r.z_det_ctrl:>+7.2f} {star(r.q_ctrl):<4}        | {surv}")
print("\n(+ = category co-occurs with higher %DET = STABILITY; − = with reorganization. Only 'survives'=YES is robust.)")
