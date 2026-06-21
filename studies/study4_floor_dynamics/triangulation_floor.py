"""Floor / turn-taking / centrality measures per 90s window, crossed with the reorg metrics.
Implements (all computable from onset+speaker+text, no audio):
  1. Participation/dominance: Gini(words), Gini(turns), participation entropy, top-speaker share
  3. Edelsky F1/F2 regime proxy: dispersion of mean turn-length ACROSS speakers (high=F1, low=F2)
  4q. Itakura quantitative dominance = top-share / Gini (folded into 1)
  2. Turn-transition network centrality: degree centralization, max eigenvector centrality, n_active
  4s/5. Sequential dominance / influence proxy: in-out degree asymmetry (who drives transitions)
Cross each vs entropy_g/det_g/rmse_g (Stouffer, within-meeting circular null). Saves floor_windows.csv."""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
GM=Path("data/metrics_gorman_l8"); TXT=Path("data/text_startup"); WIN=90
WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return WORD.findall(str(s).lower())
def gini(x):
    x=np.asarray(x,float); x=x[x>=0]
    if x.sum()==0 or len(x)<2: return np.nan
    xs=np.sort(x); n=len(x); idx=np.arange(1,n+1)
    return (2*np.sum(idx*xs)/(n*xs.sum())) - (n+1)/n
def shannon(p):
    p=np.asarray(p,float); p=p[p>0]; p=p/p.sum()
    return -(p*np.log2(p)).sum() if len(p) else 0.0
def degree_centralization(W):
    # Freeman centralization on total (in+out) degree of weighted directed graph
    N=W.shape[0]
    if N<3: return np.nan
    deg=W.sum(0)+W.sum(1); deg=deg/deg.sum() if deg.sum()>0 else deg
    dmax=deg.max(); return (dmax-deg).sum()/(N-1)
def eig_central(W):
    N=W.shape[0]
    if N<2 or W.sum()==0: return np.nan
    A=(W+W.T)/2; v=np.ones(N)/N
    for _ in range(100):
        v2=A@v; nrm=np.linalg.norm(v2)
        if nrm==0: return np.nan
        v2=v2/nrm
        if np.allclose(v2,v,atol=1e-9): break
        v=v2
    return v.max()  # dominance of the most central speaker
def inout_asym(W):
    N=W.shape[0]
    if N<2 or W.sum()==0: return np.nan
    out=W.sum(1); inn=W.sum(0); tot=W.sum()
    return np.abs(out-inn).max()/tot   # who drives transitions (initiator vs responder)

rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]).reset_index(drop=True)
    df["nw"]=df["text"].apply(lambda s:max(1,len(toks(s))))
    df["sp"]=pd.to_numeric(df["speaker_id"],errors="coerce")
    df=df.dropna(subset=["sp"]); df["sp"]=df["sp"].astype(int)
    df["bin"]=(df["onset"]//WIN*WIN).astype(int)
    g=pd.read_csv(gp); g["bin"]=(g["second"]//WIN*WIN).astype(int)
    gagg=g.groupby("bin")[["entropy_g","det_g","rmse_g"]].mean()
    for b,sub in df.groupby("bin"):
        if b not in gagg.index or len(sub)<3: continue
        sps=sorted(sub["sp"].unique()); nsp=len(sps); idx={s:i for i,s in enumerate(sps)}
        words=np.array([sub.loc[sub.sp==s,"nw"].sum() for s in sps],float)
        turns=np.array([(sub.sp==s).sum() for s in sps],float)
        meanlen=np.array([sub.loc[sub.sp==s,"nw"].mean() for s in sps],float)
        # transition network (prev->curr) within window
        seq=sub.sort_values("onset")["sp"].to_numpy()
        W=np.zeros((nsp,nsp))
        for a,c in zip(seq[:-1],seq[1:]):
            if a!=c: W[idx[a],idx[c]]+=1
        rows.append(dict(mid=mid,bin=int(b),
            entropy_g=gagg.loc[b,"entropy_g"],det_g=gagg.loc[b,"det_g"],rmse_g=gagg.loc[b,"rmse_g"],
            gini_words=gini(words),gini_turns=gini(turns),part_entropy=shannon(words),
            top_share=words.max()/words.sum() if words.sum()>0 else np.nan,
            turnlen_disp=gini(meanlen),                       # Edelsky F1/F2: high=F1, low=F2
            n_active=nsp,
            net_central=degree_centralization(W),
            eig_central=eig_central(W),
            inout_asym=inout_asym(W)))
out=pd.DataFrame(rows); out.to_csv("floor_windows.csv",index=False)
print(f"saved floor_windows.csv  rows={len(out)}  meetings={out.mid.nunique()}\n")

# ---- Stouffer cross vs reorg ----
MEAS=["gini_words","gini_turns","part_entropy","top_share","turnlen_disp","n_active",
      "net_central","eig_central","inout_asym"]
LAB={"gini_words":"Gini participation (words)","gini_turns":"Gini participation (turns)",
"part_entropy":"Participation entropy","top_share":"Top-speaker share (quant. dominance)",
"turnlen_disp":"Turn-length dispersion (Edelsky F1>F2)","n_active":"Active speakers / window",
"net_central":"Network degree centralization","eig_central":"Max eigenvector centrality",
"inout_asym":"In-out asymmetry (sequential dom./influence)"}
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
print(f"{'measure':42}|{'ENTROPY':>9}|{'%DET':>9}|{'RMSE':>9}")
print("-"*74)
for f in MEAS:
    ze,zd,zr=stf(f,'entropy_g'),stf(f,'det_g'),stf(f,'rmse_g')
    print(f"{LAB[f][:41]:42}|{ze:>+6.2f}{st(ze):<3}|{zd:>+6.2f}{st(zd):<3}|{zr:>+6.2f}{st(zr):<3}")
print("\n(+ co-varies with HIGHER metric; reorganization = entropy↑ / %DET↓ / RMSE↑)")
