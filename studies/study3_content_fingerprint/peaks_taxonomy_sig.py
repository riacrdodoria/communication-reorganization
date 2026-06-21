"""Do peaks/valleys correspond to specific taxonomy content, with significance?
Unit of inference = MEETING (n<=34). Within each meeting compare code density at
event points (peak/valley, p<.01 UCL) vs baseline points; per-meeting lift.
Across meetings: Wilcoxon signed-rank (lift!=0) + Benjamini-Hochberg FDR."""
import glob,os,json,numpy as np,pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
GM=Path(os.environ.get("GM_DIR","data/metrics_gorman_l8"))
COD2=Path("data/codebooks2"); COD1=Path("data/codebooks")
TCRIT=2.33  # p<.01 one-tailed
CATS2=['arguable','converge','disagree','delim','nonarg','iam1','iam2','iam3','iam4','iam5',
       'disput','cumul','explor','bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin',
       'basksug','bsolid','btension','bagree','bdisagree','btensh','bantag']
CATS1=['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans',
       'coop','qset','qprop','directive','commissive','feedback']
def load(folder,suf):
    d={}
    for f in glob.glob(str(folder/f"*_{suf}.json")):
        mid=os.path.basename(f).replace(f"_{suf}.json","")
        d[mid]={int(w["t"]):w for w in json.load(open(f))["windows"]}
    return d
c2=load(COD2,"passA"); c1=load(COD1,"passA")
EVENTS=[("rmse_g","peak"),("det_g","valley"),("entropy_g","peak"),("entropy_g","valley")]
# collect per-meeting lifts: lifts[(metric,side,cat)] = [lift per meeting]
from collections import defaultdict
lifts=defaultdict(list)
for f in sorted(glob.glob(str(GM/"*_gorman.csv"))):
    mid=os.path.basename(f).replace("_gorman.csv","")
    if mid not in c2: continue
    g=pd.read_csv(f); secs=g["second"].to_numpy()
    win=lambda s:int(s//90*90)
    for metric,side in EVENTS:
        x=g[metric].to_numpy(float); m=np.nanmean(x); sd=np.nanstd(x)
        mask=(x>m+TCRIT*sd) if side=="peak" else (x<m-TCRIT*sd)
        base=~mask & np.isfinite(x)
        if mask.sum()<20 or base.sum()<20: continue
        for cat in CATS2+CATS1:
            cd=c2[mid] if cat in CATS2 else c1.get(mid,{})
            dens=np.array([cd.get(win(s),{}).get(cat,0) for s in secs],float)
            if not np.isfinite(dens).any() or dens.sum()==0: continue
            lift=dens[mask].mean()-dens[base].mean()
            lifts[(metric,side,cat)].append(lift)
# test across meetings + BH-FDR within each event
def bh(pvals):
    p=np.array(pvals); n=len(p); order=np.argsort(p); ranked=p[order]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(ranked[::-1])[::-1]; out=np.empty(n); out[order]=np.clip(q,0,1); return out
ALL=[]
for metric,side in EVENTS:
    rows=[]
    for cat in CATS2+CATS1:
        L=np.array(lifts.get((metric,side,cat),[]))
        L=L[np.isfinite(L)]
        if len(L)<15: continue
        try: p=wilcoxon(L,zero_method="wilcox",alternative="two-sided").pvalue
        except: p=1.0
        rows.append(dict(cat=cat,n=len(L),mean_lift=L.mean(),pos=int((L>0).sum()),p=p))
    if not rows: continue
    df=pd.DataFrame(rows); df["q_fdr"]=bh(df["p"].tolist())
    df=df.sort_values("mean_lift",ascending=False)
    df["metric"]=metric; df["side"]=side; ALL.append(df)
    sig=df[df.q_fdr<0.05]
    print(f"\n===== {metric.upper()} {side.upper()}S — taxonomy enrichment (n meetings, BH-FDR q<.05) =====")
    if len(sig)==0: print("  (no category survives FDR)")
    for _,r in sig.iterrows():
        arrow="↑" if r.mean_lift>0 else "↓"
        print(f"  {arrow} {r['cat']:11} lift={r.mean_lift:+.3f}  {r['pos']}/{r['n']} mtgs same-dir  q={r.q_fdr:.3f}")
pd.concat(ALL,ignore_index=True).to_csv("peaks_taxonomy_sig.csv",index=False)
print("\nsaved peaks_taxonomy_sig.csv")
