"""Test: does each coding-free TEXT measure track the reorganization metrics?
Stouffer Z across meetings, within-meeting circular-shift null (like gorman_vs_content),
BH-FDR across measures within each reorg metric. + correlation among the two %DETs."""
import numpy as np,pandas as pd
from scipy.stats import pearsonr
df=pd.read_csv("triangulation_windows.csv")
MEAS=["sem_det","sem_rec","coh","nov","word_entropy","ttr","mtld","hapax","lsm",
      "turn_len","latency","transition_entropy","n_turns","connective","content_overlap"]
LAB={"sem_det":"Semantic %DET (TF-IDF recurrence)","sem_rec":"Semantic %REC",
"coh":"Turn-to-turn coherence","nov":"Novelty (topic-shift)","word_entropy":"Word entropy",
"ttr":"Type-token ratio","mtld":"MTLD lexical diversity","hapax":"Hapax ratio",
"lsm":"Language Style Matching (PT)","turn_len":"Turn length (words)","latency":"Response latency",
"transition_entropy":"Speaker-transition entropy","n_turns":"Turns per window",
"connective":"Connective density (CohM-PT)","content_overlap":"Content-word overlap (CohM-PT)"}
REORG=["entropy_g","det_g","rmse_g"]
NPERM=500; rng=np.random.default_rng(0)
def z(a):
    a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stouffer(feat,metric):
    zs=[]
    for mid,g in df.groupby("mid"):
        g=g.dropna(subset=[feat,metric])
        n=len(g)
        if n<8: continue
        zx=z(g[feat].to_numpy(float)); zy=z(g[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n
        sh=rng.integers(2,n-2,size=NPERM); idx=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[idx]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return (zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan), len(zs)
def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
from scipy.stats import norm
res={m:{} for m in REORG}
for metric in REORG:
    for feat in MEAS:
        Z,k=stouffer(feat,metric); res[metric][feat]=Z
# FDR across measures within each metric
star=lambda z:'***' if abs(z)>3.29 else '**' if abs(z)>2.58 else '*' if abs(z)>1.96 else ''
print(f"{'measure':34}| {'ENTROPY_g':>10}| {'%DET_g':>9}| {'RMSE_g':>9}")
print("-"*72)
for feat in MEAS:
    cells=[]
    for metric in REORG:
        zv=res[metric][feat]; cells.append(f"{zv:>+6.2f}{star(zv):<3}")
    print(f"{LAB[feat][:33]:34}| {cells[0]:>10}| {cells[1]:>9}| {cells[2]:>9}")
print("\n(+ = text measure co-varies with HIGHER reorg metric; *p<.05 **p<.01 ***p<.001, two-tailed)")
# headline cross: semantic %DET vs turn-taking %DET (window level, pooled within-mtg z)
zz=[]
for mid,g in df.groupby("mid"):
    g=g.dropna(subset=["sem_det","det_g"])
    if len(g)<8: continue
    a=z(g.sem_det.to_numpy(float)); b=z(g.det_g.to_numpy(float))
    if a is not None and b is not None: zz.append(np.corrcoef(a,b)[0,1])
print(f"\nHEADLINE  mean within-meeting r(semantic %DET, turn-taking %DET) = {np.nanmean(zz):+.3f}  (n={len(zz)} mtgs)")
df.to_csv("triangulation_windows.csv",index=False)
