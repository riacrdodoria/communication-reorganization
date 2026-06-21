"""Unsupervised topic segmentation (TextTiling, Hearst 1997) on TF-IDF utterance vectors.
Per meeting: cosine similarity between adjacent blocks of K utterances at each gap -> depth score ->
boundaries at deep similarity valleys. Min-episode filter. Outputs episodes_unsup.csv."""
import glob,os,re,numpy as np,pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
TXT="data/text_startup"; K=10; TARGET_LEN=50; MINSPACE=20
WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return " ".join(WORD.findall(str(s).lower()))
def segment(texts):
    n=len(texts)
    if n<2*K+2: return [0]  # too short -> one episode
    vec=TfidfVectorizer(token_pattern=r"[a-zà-ÿ]+",min_df=1)
    X=vec.fit_transform(texts).toarray()
    nrm=np.linalg.norm(X,axis=1,keepdims=True); nrm[nrm==0]=1; Xn=X/nrm
    # gap similarity between block before [i-K+1..i] and after [i+1..i+K]
    sim=np.full(n-1,np.nan)
    for i in range(n-1):
        l=Xn[max(0,i-K+1):i+1].mean(0); r=Xn[i+1:i+1+K].mean(0)
        ln=np.linalg.norm(l); rn=np.linalg.norm(r)
        sim[i]=float(l@r/(ln*rn)) if ln>0 and rn>0 else 1.0
    # smooth
    s=pd.Series(sim).rolling(3,center=True,min_periods=1).mean().to_numpy()
    # depth score at each gap
    depth=np.zeros(n-1)
    for i in range(n-1):
        lp=s[i]
        j=i
        while j>0 and s[j-1]>=s[j]: j-=1; lp=max(lp,s[j])
        lp=max(s[max(0,i-K):i+1]) if i>0 else s[i]
        rp=max(s[i:min(n-1,i+K+1)])
        depth[i]=(lp-s[i])+(rp-s[i])
    # target ~n/TARGET_LEN episodes: take the strongest depth peaks (local maxima) with min spacing
    n_target=max(3,round(n/TARGET_LEN)); n_bnd=n_target-1
    cand=[i for i in range(1,n-2) if depth[i]>=depth[i-1] and depth[i]>=depth[i+1] and depth[i]>0]
    cand.sort(key=lambda i:-depth[i])
    chosen=[]
    for i in cand:
        start=i+1
        if all(abs(start-c)>=MINSPACE for c in chosen) and start>=MINSPACE and n-start>=MINSPACE:
            chosen.append(start)
        if len(chosen)>=n_bnd: break
    return [0]+sorted(chosen)

rows=[]
for f in sorted(glob.glob(TXT+"/*_transcript.csv")):
    mid=os.path.basename(f).replace("_transcript.csv","")
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]).reset_index(drop=True)
    texts=[toks(t) for t in df["text"]]
    starts=segment(texts); starts=sorted(set(starts))
    ends=[s-1 for s in starts[1:]]+[len(df)-1]
    for ep,(a,b) in enumerate(zip(starts,ends)):
        rows.append(dict(mid=mid,episode=ep,utt_start=a,utt_end=b,n_utt=b-a+1,
            sec_start=float(df["onset"].iloc[a]),sec_end=float(df["onset"].iloc[b])))
E=pd.DataFrame(rows); E.to_csv("episodes_unsup.csv",index=False)
per=E.groupby("mid").size()
print(f"saved episodes_unsup.csv | {E.mid.nunique()} meetings | episodes/meeting: "
      f"median={per.median():.0f} mean={per.mean():.1f} range=[{per.min()},{per.max()}]")
print(f"episode length (utterances): median={E.n_utt.median():.0f}  "
      f"duration(s): median={(E.sec_end-E.sec_start).median():.0f}")
