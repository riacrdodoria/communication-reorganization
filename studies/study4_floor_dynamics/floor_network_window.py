"""(c) Strengthen the network-centrality measures: recompute on LARGER windows (300 s) and on the
WHOLE meeting, since 90 s windows hold too few turns for stable graphs.
- 300 s windows: re-cross with reorg (Stouffer, within-meeting circular null).
- per-meeting whole network: correlate centralization with meeting-level reorg summaries (n=34)."""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
from scipy.stats import pearsonr
GM=Path("data/metrics_gorman_l8"); TXT=Path("data/text_startup")
# 2026-09-05: measures moved to floor_measures.py (normalised centralization, Perron eigenvector, dyadic asymmetry)
from floor_measures import degree_centralization, eig_central, inout_asym
def build_W(seq,idx,nsp):
    W=np.zeros((nsp,nsp))
    for a,c in zip(seq[:-1],seq[1:]):
        if a!=c: W[idx[a],idx[c]]+=1
    return W

def load(f):
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]); df["sp"]=pd.to_numeric(df["speaker_id"],errors="coerce")
    return df.dropna(subset=["sp"]).assign(sp=lambda x:x.sp.astype(int)).sort_values("onset").reset_index(drop=True)

# ---- 300 s window cross ----
WIN=300; rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=load(f); df["bin"]=(df["onset"]//WIN*WIN).astype(int)
    g=pd.read_csv(gp); g["bin"]=(g["second"]//WIN*WIN).astype(int)
    gagg=g.groupby("bin")[["entropy_g","det_g","rmse_g"]].mean()
    for b,sub in df.groupby("bin"):
        if b not in gagg.index or len(sub)<8: continue
        sps=sorted(sub.sp.unique()); idx={s:i for i,s in enumerate(sps)}
        W=build_W(sub.sp.to_numpy(),idx,len(sps))
        rows.append(dict(mid=mid,entropy_g=gagg.loc[b,"entropy_g"],det_g=gagg.loc[b,"det_g"],
            rmse_g=gagg.loc[b,"rmse_g"],net_central=degree_centralization(W),
            eig_central=eig_central(W),inout_asym=inout_asym(W)))
D=pd.DataFrame(rows)
NP=500; rng=np.random.default_rng(0)
def z(a): a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stf(df,feat,metric):
    zs=[]
    for mid,gg in df.groupby("mid"):
        gg=gg.dropna(subset=[feat,metric]); n=len(gg)
        if n<8: continue
        zx=z(gg[feat].to_numpy(float)); zy=z(gg[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n; sh=rng.integers(2,n-2,size=NP); ix=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[ix]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
star=lambda z:'***' if abs(z)>3.29 else '**' if abs(z)>2.58 else '*' if abs(z)>1.96 else ''
print(f"=== 300 s windows (n={len(D)}): network measures re-crossed vs reorg ===")
print(f"{'measure':30}|{'ENTROPY':>9}|{'%DET':>9}|{'RMSE':>9}")
for f in ["net_central","eig_central","inout_asym"]:
    ze,zd,zr=stf(D,f,'entropy_g'),stf(D,f,'det_g'),stf(D,f,'rmse_g')
    print(f"{f:30}|{ze:>+6.2f}{star(ze):<3}|{zd:>+6.2f}{star(zd):<3}|{zr:>+6.2f}{star(zr):<3}")

# ---- per-meeting whole network vs meeting-level reorg ----
mrows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=load(f); sps=sorted(df.sp.unique()); idx={s:i for i,s in enumerate(sps)}
    W=build_W(df.sp.to_numpy(),idx,len(sps))
    g=pd.read_csv(gp)
    mrows.append(dict(mid=mid,n_sp=len(sps),
        net_central=degree_centralization(W),eig_central=eig_central(W),inout_asym=inout_asym(W),
        mean_entropy=g.entropy_g.mean(),mean_det=g.det_g.mean(),mean_rmse=g.rmse_g.mean()))
M=pd.DataFrame(mrows)
print(f"\n=== per-meeting whole network (n={len(M)}) vs meeting-level reorg (Pearson r, p) ===")
for f in ["net_central","eig_central","inout_asym"]:
    for m in ["mean_entropy","mean_det","mean_rmse"]:
        sub=M.dropna(subset=[f,m])
        r,p=pearsonr(sub[f],sub[m])
        sig='*' if p<.05 else ''
        print(f"  {f:14} vs {m:13} r={r:+.3f} p={p:.3f}{sig}")
M.to_csv("floor_network_meeting.csv",index=False)
print("\nsaved floor_network_meeting.csv")
