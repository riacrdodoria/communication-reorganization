"""Decisive check: do the STRICT-Gorman metrics replicate the content map?
Correlate codebooks2 categories with entropy_g/det_g/rmse_g (window-mean over 90s),
Stouffer within-meeting circular null. Compare RMSE story old vs new."""
import glob,os,json,numpy as np,pandas as pd
from pathlib import Path
GM=Path(os.environ.get("GM_DIR","data/metrics_gorman")); COD=Path("data/codebooks2"); MET=Path("data/processed/metrics_startup")
CATS=["arguable","disagree","iam2","bdisagree","explor","disput","delim","iam1","converge","bagree","baskinfo","qset" if False else "nonarg","cumul"]
CATS=["arguable","disagree","iam2","bdisagree","explor","disput","delim","iam1","arguable","converge","bagree","cumul","nonarg"]
CATS=sorted(set(["arguable","disagree","iam2","bdisagree","explor","disput","delim","iam1","converge","bagree","cumul","nonarg","baskinfo"]))
NPERM=400; rng=np.random.default_rng(0)
def load(f): d=json.load(open(f)); return {int(w["t"]):w for w in d["windows"]}
def z(a):
    a=a-a.mean(); s=a.std(); return a/s if s>0 else None
def stouffer(df,feat,metric):
    zs=[]
    for mid,g in df.groupby("mid"):
        n=len(g)
        if n<8: continue
        zx=z(g[feat].to_numpy(float)); zy=z(g[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n
        sh=rng.integers(2,n-2,size=NPERM); idx=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[idx]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
rows=[]
for f in sorted(glob.glob(str(COD/"*_passA.json"))):
    mid=os.path.basename(f).replace("_passA.json","")
    gp=GM/f"{mid}_gorman.csv"; op=MET/f"{mid}_entropy.csv"
    if not gp.exists() or not op.exists(): continue
    G=pd.read_csv(gp).set_index("second"); O=pd.read_csv(op).set_index("second")
    cod=load(f)
    for t,w in cod.items():
        gg=G[(G.index>=t)&(G.index<t+90)]; oo=O[(O.index>=t)&(O.index<t+90)]
        if len(gg)<20 or len(oo)<20: continue
        r=dict(mid=mid,
            ent_g=gg.entropy_g.mean(),det_g=gg.det_g.mean(),rmse_g=gg.rmse_g.mean(),
            rmse_old=oo.rmse_lsh.mean(),ent_old=oo.entropy_lsh.mean())
        for c in CATS: r[c]=w.get(c,0)
        rows.append(r)
df=pd.DataFrame(rows).dropna()
star=lambda z:'***' if abs(z)>3.29 else '**' if abs(z)>2.58 else '*' if abs(z)>1.96 else ''
print(f"n windows={len(df)}\n")
print(f"{'category':14}| {'RMSE_old':>9}| {'RMSE_g(new)':>11}| {'ENT_g':>8}| {'DET_g':>8}")
print("-"*60)
for c in CATS:
    zro=stouffer(df,c,'rmse_old'); zrn=stouffer(df,c,'rmse_g'); ze=stouffer(df,c,'ent_g'); zd=stouffer(df,c,'det_g')
    print(f"{c:14}| {zro:>+6.2f}{star(zro):<3}| {zrn:>+6.2f}{star(zrn):<5}| {ze:>+5.2f}{star(ze):<3}| {zd:>+5.2f}{star(zd):<3}")
# correlation old vs new rmse at window level
from scipy.stats import pearsonr
print(f"\ncorr(rmse_old, rmse_g) window-level = {pearsonr(df.rmse_old,df.rmse_g)[0]:+.3f}")
print(f"corr(ent_old, ent_g)   window-level = {pearsonr(df.ent_old,df.ent_g)[0]:+.3f}")
