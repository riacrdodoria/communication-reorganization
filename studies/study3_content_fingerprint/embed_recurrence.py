"""Robustness check for Study 3: semantic recurrence computed with multilingual sentence EMBEDDINGS
instead of TF-IDF. Mirrors triangulation_build.py but captures paraphrase/synonymy, so it tests whether
the TF-IDF conceptual-recurrence result is robust to the representation. Outputs embedding_windows.csv
and prints Stouffer Z vs entropy_g/det_g/rmse_g.

Requirements: pip install sentence-transformers pandas scipy scikit-learn (CPU is sufficient).
Inputs: the (withheld) transcript files data/text_startup/*.csv and data/metrics_gorman_l8/*.csv.
"""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
TXT=Path("data/text_startup"); GM=Path("data/metrics_gorman_l8"); WIN=90
MODEL=os.environ.get("EMB_MODEL","sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
RADIUS=float(os.environ.get("EMB_RADIUS","0.5"))  # cosine recurrence threshold in embedding space
WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return WORD.findall(str(s).lower())
def det_from_R(R,lmin=2):
    n=R.shape[0]; iu=np.triu_indices(n,1); rec=int(R[iu].sum())
    if rec==0: return 0.0,0.0
    tot=0
    for off in range(1,n):
        d=np.diagonal(R,off); run=0
        for v in d:
            if v: run+=1
            else:
                if run>=lmin: tot+=run
                run=0
        if run>=lmin: tot+=run
    return 100.0*tot/rec,100.0*rec/len(iu[0])

from sentence_transformers import SentenceTransformer
print(f"loading {MODEL} ...",flush=True)
enc=SentenceTransformer(MODEL)

rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=pd.read_csv(f); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]).reset_index(drop=True)
    df["nw"]=df["text"].apply(lambda s:max(1,len(toks(s))))
    df["bin"]=(df["onset"]//WIN*WIN).astype(int)
    E=enc.encode(df["text"].astype(str).tolist(),normalize_embeddings=True,show_progress_bar=False)
    E=np.asarray(E)
    coh=np.full(len(df),np.nan); nov=np.full(len(df),np.nan)
    for i in range(1,len(df)):
        coh[i]=float(E[i]@E[i-1]); k0=max(0,i-5)
        nov[i]=1-max((float(E[i]@E[j]) for j in range(k0,i)),default=0.0)
    df["coh"]=coh; df["nov"]=nov
    g=pd.read_csv(gp); g["bin"]=(g["second"]//WIN*WIN).astype(int)
    gagg=g.groupby("bin")[["entropy_g","det_g","rmse_g"]].mean()
    for b,sub in df.groupby("bin"):
        if b not in gagg.index or len(sub)<3: continue
        V=E[sub.index.to_numpy()]; S=V@V.T; R=(S>=RADIUS).astype(int); np.fill_diagonal(R,0)
        sdet,srec=det_from_R(R)
        rows.append(dict(mid=mid,bin=int(b),entropy_g=gagg.loc[b,"entropy_g"],
            det_g=gagg.loc[b,"det_g"],rmse_g=gagg.loc[b,"rmse_g"],
            esem_det=sdet,esem_rec=srec,ecoh=np.nanmean(sub["coh"]),enov=np.nanmean(sub["nov"])))
    print(f"  {mid}: {sum(1 for r in rows if r['mid']==mid)} windows",flush=True)
out=pd.DataFrame(rows); out.to_csv("embedding_windows.csv",index=False)
print(f"saved embedding_windows.csv rows={len(out)}")
# Stouffer vs reorg
NP=500; rng=np.random.default_rng(0)
def z(a): a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stf(feat,metric):
    zs=[]
    for mid,gg in out.groupby("mid"):
        gg=gg.dropna(subset=[feat,metric]); n=len(gg)
        if n<8: continue
        zx=z(gg[feat].to_numpy(float)); zy=z(gg[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n; sh=rng.integers(2,n-2,size=NP); idx=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[idx]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
st=lambda z:'***' if abs(z)>3.29 else '**' if abs(z)>2.58 else '*' if abs(z)>1.96 else ''
print(f"\n{'embedding measure':28}|{'ENTROPY':>9}|{'%DET':>9}|{'RMSE':>9}")
for f,lab in [("esem_det","semantic %DET (emb)"),("esem_rec","semantic %REC (emb)"),
              ("ecoh","coherence (emb)"),("enov","novelty (emb)")]:
    print(f"{lab:28}|{stf(f,'entropy_g'):>+6.2f}{st(stf(f,'entropy_g')):<3}|{stf(f,'det_g'):>+6.2f}{st(stf(f,'det_g')):<3}|{stf(f,'rmse_g'):>+6.2f}{st(stf(f,'rmse_g')):<3}")
