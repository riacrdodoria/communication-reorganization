"""Gorman-style peak/valley detection on reorganization series + peak-locked content.
Peaks: metric > UCL = mean + t*SD (within meeting). t=1.65 (p<.05), 2.33 (p<.01).
Then: do content codes (from validated codebooks) differ in peak windows vs baseline?
Map each 1s metric point to the 90s content window it falls in."""
from __future__ import annotations
import glob,os,json,numpy as np,pandas as pd
from pathlib import Path
from scipy.stats import mannwhitneyu

GM=Path(os.environ.get("GM_DIR","data/metrics_gorman")); COD=Path("data/codebooks2"); COD1=Path("data/codebooks")
TCRIT={"p05":1.65,"p01":2.33}

def peaks(x,t):
    x=np.asarray(x,float); m=np.nanmean(x); sd=np.nanstd(x)
    ucl=m+t*sd; lcl=m-t*sd
    return (x>ucl), (x<lcl), ucl

def load_codes(folder,suf):
    d={}
    for f in glob.glob(str(folder/f"*_{suf}.json")):
        mid=os.path.basename(f).replace(f"_{suf}.json","")
        j=json.load(open(f)); d[mid]={int(w["t"]):w for w in j["windows"]}
    return d

def main():
    codes=load_codes(COD,"passA")      # CACS/IAM/Mercer/Bales
    codes1=load_codes(COD1,"passA")    # act4teams-SHORT + ISO
    CATS2=["arguable","disagree","iam2","disput","explor","bdisagree","converge","bagree","baskinfo","cumul","nonarg"]
    CATS1=["qset","qprop","feedback","namep","names","proact","struct"]
    # per-meeting peak counts
    summ=[]
    pooled={m:{"peak":[],"base":[]} for m in ["entropy_g","det_g","rmse_g"]}
    catrows=[]
    for f in sorted(glob.glob(str(GM/"*_gorman.csv"))):
        mid=os.path.basename(f).replace("_gorman.csv","")
        g=pd.read_csv(f)
        c2=codes.get(mid,{}); c1=codes1.get(mid,{})
        if not c2: continue
        def win(sec): return int(sec//90*90)
        for metric in ["entropy_g","det_g","rmse_g"]:
            x=g[metric].to_numpy(float)
            pk,vl,ucl=peaks(x,TCRIT["p01"])
            npk=int(np.nansum(pk)); nvl=int(np.nansum(vl))
            summ.append(dict(mid=mid,metric=metric,n=len(x),peaks=npk,valleys=nvl,pct_peak=100*npk/len(x)))
            # peak-locked content: for each metric point, code density of its 90s window
            for cat,src in [(c,2) for c in CATS2]+[(c,1) for c in CATS1]:
                cd=c2 if src==2 else c1
                vals_pk=[]; vals_base=[]
                for i,sec in enumerate(g["second"]):
                    w=cd.get(win(sec))
                    if w is None: continue
                    v=w.get(cat,0)
                    (vals_pk if pk[i] else vals_base).append(v)
                if len(vals_pk)>=20 and len(vals_base)>=20 and (np.mean(vals_pk)+np.mean(vals_base))>0:
                    catrows.append(dict(metric=metric,cat=cat,
                        mpk=np.mean(vals_pk),mbase=np.mean(vals_base),
                        lift=np.mean(vals_pk)-np.mean(vals_base)))
    S=pd.DataFrame(summ)
    print("=== PEAK/VALLEY rates (p<.01 UCL, mean over 34 meetings) ===")
    print(S.groupby("metric")[["peaks","valleys","pct_peak"]].mean().round(2).to_string())
    C=pd.DataFrame(catrows)
    print("\n=== PEAK-LOCKED CONTENT: mean code LIFT in peak vs baseline windows (avg over meetings) ===")
    agg=C.groupby(["metric","cat"]).lift.mean().reset_index()
    for metric in ["rmse_g","entropy_g","det_g"]:
        sub=agg[agg.metric==metric].sort_values("lift",ascending=False)
        print(f"\n-- {metric}: codes MOST enriched at peaks --")
        for _,r in sub.head(6).iterrows(): print(f"   {r['lift']:+.3f}  {r['cat']}")
    C.to_csv("peaks_content_lift.csv",index=False); S.to_csv("peaks_summary.csv",index=False)
    print("\nsaved peaks_summary.csv, peaks_content_lift.csv")

if __name__=="__main__": main()
