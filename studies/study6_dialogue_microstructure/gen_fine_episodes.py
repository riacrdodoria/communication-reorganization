import glob,os,re,numpy as np,pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
TXT="data/text_startup"; TL=18; K=10
WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return " ".join(WORD.findall(str(s).lower()))
def segment(texts,target_len=TL,minspace=9):
    n=len(texts)
    if n<2*K+2: return [0]
    X=TfidfVectorizer(token_pattern=r"[a-zà-ÿ]+",min_df=1).fit_transform(texts).toarray()
    nrm=np.linalg.norm(X,axis=1,keepdims=True); nrm[nrm==0]=1; Xn=X/nrm
    s=np.array([(Xn[max(0,i-K+1):i+1].mean(0)@Xn[i+1:i+1+K].mean(0))/
        ((np.linalg.norm(Xn[max(0,i-K+1):i+1].mean(0))+1e-9)*(np.linalg.norm(Xn[i+1:i+1+K].mean(0))+1e-9))
        for i in range(n-1)])
    s=pd.Series(s).rolling(3,center=True,min_periods=1).mean().to_numpy()
    depth=np.array([(max(s[max(0,i-K):i+1])-s[i])+(max(s[i:min(n-1,i+K+1)])-s[i]) for i in range(n-1)])
    n_bnd=max(2,round(n/target_len))-1
    cand=[i for i in range(1,n-2) if depth[i]>=depth[i-1] and depth[i]>=depth[i+1] and depth[i]>0]
    cand.sort(key=lambda i:-depth[i]); chosen=[]
    for i in cand:
        st=i+1
        if all(abs(st-c)>=minspace for c in chosen) and st>=minspace and n-st>=minspace: chosen.append(st)
        if len(chosen)>=n_bnd: break
    return [0]+sorted(chosen)
rows=[]
for f in sorted(glob.glob(TXT+"/*_transcript.csv")):
    mid=os.path.basename(f).replace("_transcript.csv","")
    df=pd.read_csv(f); df=df.assign(onset=pd.to_numeric(df["onset_seconds"],errors="coerce")).dropna(subset=["onset"]).reset_index(drop=True)
    st=segment([toks(t) for t in df["text"]]); ends=[s-1 for s in st[1:]]+[len(df)-1]
    for ep,(a,b) in enumerate(zip(st,ends)):
        rows.append(dict(mid=mid,ep=ep,utt_start=a,utt_end=b,n_utt=b-a+1))
E=pd.DataFrame(rows); E.to_csv("data/episodes_fine.csv",index=False)
print(f"saved data/episodes_fine.csv | {E.mid.nunique()} mtgs | {len(E)} episodes | median {E.groupby('mid').size().median():.0f} eps/mtg, {E.n_utt.median():.0f} utt/ep")
