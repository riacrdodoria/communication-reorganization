"""(b) Influence Model (Basu/Choudhury/Pentland) per meeting, fully-observed estimation.
Each speaker = a binary speaking chain b_i(t) at 1 s. The influence parameter alpha_{i->j} weights how
much chain i's current state predicts chain j's NEXT state, fit per target j by non-negative least
squares on the convex combination of pairwise conditional predictors, then normalized to sum 1.
Outputs per meeting: outgoing influence per speaker, the dominant influencer, and influence
centralization (Gini of outgoing influence) — related to meeting-level reorganization (n=34).
NOTE: fully-observed estimation (states are known), so no EM/latent states needed."""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
from scipy.optimize import nnls
from scipy.stats import pearsonr
GM=Path("data/metrics_gorman_l8"); TXT=Path("data/text_startup")
WORD=re.compile(r"[a-zà-ÿ]+")
def nw(s): return max(1,len(WORD.findall(str(s).lower())))
def gini(x):
    x=np.asarray(x,float); x=x[x>=0]
    if x.sum()==0 or len(x)<2: return np.nan
    xs=np.sort(x); n=len(x); idx=np.arange(1,n+1)
    return (2*np.sum(idx*xs)/(n*xs.sum()))-(n+1)/n

def speaking_matrix(df):
    sps=sorted(df.sp.unique()); idx={s:i for i,s in enumerate(sps)}
    T=int(np.ceil(df["onset"].max()+ df["nwd"].iloc[-1]*0.5))+2
    B=np.zeros((len(sps),T),dtype=int)
    for r in df.itertuples():
        a=int(np.floor(r.onset)); b=int(np.ceil(r.onset+0.5*r.nwd))
        B[idx[r.sp],a:max(b,a+1)]=1
    return B,sps

def influence(B):
    N,T=B.shape
    cur=B[:,:-1]; nxt=B[:,1:]           # state at t, t+1
    alpha=np.zeros((N,N))               # alpha[i,j] = influence of i on j
    for j in range(N):
        y=nxt[j].astype(float)
        # predictor from chain i = P(y_j=1 | state of i) evaluated at each t
        P=np.zeros((T-1,N))
        for i in range(N):
            for s in (0,1):
                m=cur[i]==s
                P[m,i]= y[m].mean() if m.sum()>0 else 0.0
        a,_=nnls(P,y)
        if a.sum()>0: a=a/a.sum()
        alpha[:,j]=a
    return alpha

rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]); df["sp"]=pd.to_numeric(df["speaker_id"],errors="coerce")
    df=df.dropna(subset=["sp"]).assign(sp=lambda x:x.sp.astype(int))
    df["nwd"]=df["text"].apply(nw); df=df.sort_values("onset").reset_index(drop=True)
    B,sps=speaking_matrix(df)
    if B.shape[1]<40 or len(sps)<2: continue
    A=influence(B)
    np.fill_diagonal(A,0)                       # outgoing influence on OTHERS
    out_inf=A.sum(1)                            # how much each speaker drives others
    g=pd.read_csv(gp)
    rows.append(dict(mid=mid,n_sp=len(sps),
        infl_central=gini(out_inf),
        top_influencer_share=out_inf.max()/out_inf.sum() if out_inf.sum()>0 else np.nan,
        mean_entropy=g.entropy_g.mean(),mean_det=g.det_g.mean(),mean_rmse=g.rmse_g.mean()))
M=pd.DataFrame(rows); M.to_csv("influence_meeting.csv",index=False)
print(f"Influence Model fit on {len(M)} meetings.  (alpha_ij per meeting; outgoing influence per speaker)\n")
print("Influence centralization (Gini of outgoing influence) summary:")
print(f"  mean={M.infl_central.mean():.3f}  range=[{M.infl_central.min():.3f}, {M.infl_central.max():.3f}]")
print(f"\n=== meeting-level influence vs reorganization (Pearson r, p; n={len(M)}) ===")
for f in ["infl_central","top_influencer_share"]:
    for m in ["mean_entropy","mean_det","mean_rmse"]:
        sub=M.dropna(subset=[f,m]); r,p=pearsonr(sub[f],sub[m])
        print(f"  {f:20} vs {m:13} r={r:+.3f} p={p:.3f}{'*' if p<.05 else ''}")
print("\nsaved influence_meeting.csv")
