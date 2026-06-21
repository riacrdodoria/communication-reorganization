"""Granularity sweep for topic segmentation: fine -> coarse.
For each target episode length, segment all 34 meetings (TextTiling) and measure:
  (1) boundary-as-perturbation effect (entropy↑/%DET↓ at ±30s of boundaries vs interior)
  (2) taxonomy structure captured = eta² (between-episode variance ratio) of category density,
      reported as EXCESS over random boundaries (controls for mechanical inflation with more episodes)
  (3) per-episode metric reliability (median turns/episode, % episodes too short)."""
import glob,os,re,json,numpy as np,pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import wilcoxon
TXT="data/text_startup"; GM="data/metrics_gorman_l8"; COD2="data/codebooks2"; COD1="data/codebooks"
WORD=re.compile(r"[a-zà-ÿ]+"); rng=np.random.default_rng(0)
def toks(s): return " ".join(WORD.findall(str(s).lower()))
def segment(texts,target_len,K=10,minspace=None):
    n=len(texts)
    if minspace is None: minspace=max(8,target_len//2)
    if n<2*K+2: return [0]
    X=TfidfVectorizer(token_pattern=r"[a-zà-ÿ]+",min_df=1).fit_transform(texts).toarray()
    nrm=np.linalg.norm(X,axis=1,keepdims=True); nrm[nrm==0]=1; Xn=X/nrm
    sim=np.array([ (Xn[max(0,i-K+1):i+1].mean(0)@Xn[i+1:i+1+K].mean(0))/
        ((np.linalg.norm(Xn[max(0,i-K+1):i+1].mean(0))+1e-9)*(np.linalg.norm(Xn[i+1:i+1+K].mean(0))+1e-9))
        for i in range(n-1)])
    s=pd.Series(sim).rolling(3,center=True,min_periods=1).mean().to_numpy()
    depth=np.array([ (max(s[max(0,i-K):i+1])-s[i])+(max(s[i:min(n-1,i+K+1)])-s[i]) for i in range(n-1)])
    n_bnd=max(2,round(n/target_len))-1
    cand=[i for i in range(1,n-2) if depth[i]>=depth[i-1] and depth[i]>=depth[i+1] and depth[i]>0]
    cand.sort(key=lambda i:-depth[i]); chosen=[]
    for i in cand:
        st=i+1
        if all(abs(st-c)>=minspace for c in chosen) and st>=minspace and n-st>=minspace: chosen.append(st)
        if len(chosen)>=n_bnd: break
    return [0]+sorted(chosen)
def load_cod(folder,suf):
    d={}
    for f in glob.glob(f"{folder}/*_{suf}.json"):
        mid=os.path.basename(f).replace(f"_{suf}.json","")
        d[mid]=pd.DataFrame(json.load(open(f))["windows"])
    return d
c2=load_cod(COD2,"passA"); c1=load_cod(COD1,"passA")
CATS={"arguable":c2,"converge":c2,"nonarg":c2,"disagree":c2,"explor":c2,"ktrans":c1,"bgiveopin":c2,
      "feedback":c1,"baskinfo":c2,"bagree":c2,"struct":c1,"qprop":c1,"iam4":c2}
def eta2(densdf,ep_of_window):
    # densdf: per-window category density; ep_of_window: episode id per window
    vals=[]
    for c,_ in CATS.items():
        if c not in densdf: continue
        x=densdf[c].to_numpy(float); g=ep_of_window
        if len(x)<4 or np.nanstd(x)==0: continue
        gm=np.nanmean(x); sst=np.nansum((x-gm)**2)
        ssb=0
        for e in np.unique(g):
            xe=x[g==e]; ssb+=len(xe)*(np.nanmean(xe)-gm)**2
        if sst>0: vals.append(ssb/sst)
    return np.mean(vals) if vals else np.nan

# preload transcripts + metrics + window densities
DATA={}
for f in sorted(glob.glob(TXT+"/*_transcript.csv")):
    mid=os.path.basename(f).replace("_transcript.csv","")
    if mid not in c2 or not os.path.exists(f"{GM}/{mid}_gorman.csv"): continue
    df=pd.read_csv(f); on=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.assign(onset=on).dropna(subset=["onset"]).reset_index(drop=True)
    g=pd.read_csv(f"{GM}/{mid}_gorman.csv")
    cd=c2[mid].copy()
    if mid in c1.index if hasattr(c1,'index') else mid in c1:
        cd=cd.merge(c1[mid],on="t",how="outer") if False else cd
    cdd=c2[mid].merge(c1[mid][["t"]+[c for c in CATS if c in c1[mid].columns]],on="t",how="left") if mid in c1 else c2[mid]
    DATA[mid]=dict(texts=[toks(t) for t in df["text"]], onset=df["onset"].to_numpy(),
                   sec=g["second"].to_numpy(), ent=g.entropy_g.to_numpy(float), det=g.det_g.to_numpy(float), cw=cdd)

print(f"{'target_len':>10} {'eps/mtg':>8} {'med turns':>9} | {'Δent_bnd':>8} {'Δdet_bnd':>8} (p) | {'eta²obs':>7} {'eta²rand':>8} {'EXCESS':>7}")
for TL in [15,25,40,60,90]:
    epc=[]; turns=[]; be=[]; bd=[]; etao=[]; etar=[]
    for mid,D in DATA.items():
        st=segment(D["texts"],TL); st=sorted(set(st)); n=len(D["texts"])
        bounds_utt=st[1:]; epc.append(len(st))
        ends=[s-1 for s in st[1:]]+[n-1]
        for a,b in zip(st,ends): turns.append(b-a+1)
        bsec=[float(D["onset"][i]) for i in bounds_utt if i<len(D["onset"])]
        sec=D["sec"]; inb=np.zeros(len(sec),bool)
        for t in bsec: inb|=(np.abs(sec-t)<=30)
        if inb.sum()>=10 and (~inb).sum()>=10:
            be.append(D["ent"][inb].mean()-D["ent"][~inb].mean()); bd.append(D["det"][inb].mean()-D["det"][~inb].mean())
        # eta2: assign each 90s window to episode by its time t
        cw=D["cw"]; wt=cw["t"].to_numpy()
        ep_bounds=[float(D["onset"][i]) for i in st]  # episode start seconds
        ep_of=np.searchsorted(ep_bounds,wt,side="right")-1
        etao.append(eta2(cw,ep_of))
        # random boundaries same count
        nb=len(bounds_utt)
        if nb>0 and n>2*nb+4:
            rb=sorted(rng.choice(range(2,n-2),size=nb,replace=False))
            rstarts=[0]+rb; rsec=[float(D["onset"][i]) for i in rstarts if i<len(D["onset"])]
            ep_of_r=np.searchsorted(sorted(rsec),wt,side="right")-1
            etar.append(eta2(cw,ep_of_r))
    pe=wilcoxon(be).pvalue if len(be)>=8 else 1
    eo=np.nanmean(etao); er=np.nanmean(etar)
    print(f"{TL:>10} {np.mean(epc):>8.1f} {np.median(turns):>9.0f} | {np.mean(be):>+8.2f} {np.mean(bd):>+8.2f} (p={pe:.3f}) | {eo:>7.3f} {er:>8.3f} {eo-er:>+7.3f}")
print("\n(best = high boundary effect + high eta² EXCESS over random; turns/episode too low = noisy metrics)")
