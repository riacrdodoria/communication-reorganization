"""Proper bimodality test: is the within-meeting metric cloud TWO modes or one continuum?
Null = single multivariate Gaussian with same covariance (unimodal, preserves correlation).
If observed k=2 silhouette ~ Gaussian-null silhouette -> NO real two clusters."""
import glob,os,numpy as np,pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
GM=Path(os.environ.get("GM_DIR","data/metrics_gorman")); MET=Path("data/processed/metrics_startup")
rng=np.random.default_rng(0)
def build(which):
    rows=[]
    for f in sorted(glob.glob(str(GM/"*_gorman.csv"))):
        mid=os.path.basename(f).replace("_gorman.csv","")
        g=pd.read_csv(f); o=pd.read_csv(MET/f"{mid}_entropy.csv")
        d=(g[["entropy_g","det_g","rmse_g"]] if which=="new" else o[["entropy_lsh","det_lsh","rmse_lsh"]]).copy()
        d.columns=["e","d","r"]; d=d.dropna()
        if len(d)<30: continue
        d=(d-d.mean())/d.std(ddof=0); rows.append(d)
    X=pd.concat(rows,ignore_index=True)[["e","d","r"]].to_numpy(float)
    return X[np.isfinite(X).all(1)]
def dip_stat(x):  # simple Hartigan dip via max gap of ECDF vs best unimodal (approx: use kurtosis+gap)
    x=np.sort(x); n=len(x); ecdf=np.arange(1,n+1)/n
    # bimodality coefficient (Sarle): b=(skew^2+1)/kurt ; >0.555 suggests bimodal
    from scipy.stats import skew,kurtosis
    s=skew(x); k=kurtosis(x,fisher=True)+3
    return (s**2+1)/k
def gauss_null_sil(X,reps=30):
    mu=X.mean(0); cov=np.cov(X.T); sils=[]
    for _ in range(reps):
        Xn=rng.multivariate_normal(mu,cov,size=len(X))
        l=KMeans(2,n_init=5,random_state=0).fit_predict(Xn); sils.append(silhouette_score(Xn,l))
    return np.array(sils)
for name,w in [("OLD (rmse_lsh)","old"),("NEW (Gorman-verified)","new")]:
    X=build(w)
    idx=rng.choice(len(X),min(4000,len(X)),replace=False); Xs=X[idx]
    km=KMeans(2,n_init=10,random_state=0).fit(Xs); sil=silhouette_score(Xs,km.labels_)
    gn=gauss_null_sil(Xs)
    pc1=PCA(3).fit_transform(Xs)[:,0]
    bc=dip_stat(pc1)
    print(f"\n=== {name} ===")
    print(f"  k=2 silhouette        = {sil:.3f}")
    print(f"  unimodal-Gaussian null= {gn.mean():.3f} +/- {gn.std():.3f}   p(null>=obs)={(gn>=sil).mean():.3f}")
    print(f"  -> {'REAL two modes (obs >> unimodal null)' if sil>gn.mean()+2*gn.std() else 'NO real two modes: a single continuum (k-means splits a 1-mode cloud just like a Gaussian does)'}")
    print(f"  bimodality coefficient (PC1) = {bc:.3f}  (>0.555 hints bimodal; ~0.33 = normal/unimodal)")
