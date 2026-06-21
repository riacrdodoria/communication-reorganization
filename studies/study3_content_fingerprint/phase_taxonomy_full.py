"""All taxonomy categories x the 4 reorganization phases (ascending/peak/descending/valley).
Phases from entropy_g. Per meeting: mean category density per phase. Tests:
  - PEAK vs VALLEY (the resolvable extremes = reorganization vs stability), paired Wilcoxon + BH-FDR.
  - ASCENDING vs DESCENDING (expected null at 90s content resolution; reported for honesty).
Grouped by taxonomy. Output numeric only."""
import glob,os,re,json,numpy as np,pandas as pd
from scipy.stats import wilcoxon
GM="data/metrics_gorman_l8"; COD2="data/codebooks2"; COD1="data/codebooks"
TAX={
"CACS":["arguable","converge","disagree","delim","nonarg"],
"Bales IPA":["bgiveinfo","bgiveopin","bgivesug","baskinfo","baskopin","basksug","bsolid","btension","bagree","bdisagree","btensh","bantag"],
"ISO 24617-2":["qset","qprop","directive","commissive","feedback"],
"act4teams":["proact","struct","coop","cprod","ginfo","ktrans","namep","names","linkp","links","linkc"],
"Gunawardena IAM":["iam1","iam2","iam3","iam4","iam5"],
"Mercer":["disput","cumul","explor"]}
SET1={"qset","qprop","directive","commissive","feedback","proact","struct","coop","cprod","ginfo","ktrans","namep","names","linkp","links","linkc"}
def load(folder,suf):
    d={}
    for f in glob.glob(f"{folder}/*_{suf}.json"):
        mid=os.path.basename(f).replace(f"_{suf}.json","")
        d[mid]={int(w["t"]):w for w in json.load(open(f))["windows"]}
    return d
c2=load(COD2,"passA"); c1=load(COD1,"passA")
def phases(s):
    m,sd=np.nanmean(s),np.nanstd(s); dd=np.gradient(s); lab=np.empty(len(s),dtype=object)
    for i,v in enumerate(s):
        lab[i]="peak" if v>m+0.8*sd else "valley" if v<m-0.8*sd else ("ascending" if dd[i]>0 else "descending")
    return lab
ALL=[c for cs in TAX.values() for c in cs]
store={c:{p:[] for p in ["ascending","peak","descending","valley"]} for c in ALL}
for f in sorted(glob.glob(GM+"/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    if mid not in c2: continue
    g=pd.read_csv(f); ent=g.entropy_g.to_numpy(float); sec=g["second"].to_numpy(); lab=phases(ent)
    win=lambda s:int(s//90*90)
    for c in ALL:
        src=(c1 if c in SET1 else c2).get(mid,{})
        dens=np.array([src.get(win(s),{}).get(c,0) for s in sec],float)
        for p in store[c]:
            mask=lab==p
            store[c][p].append(dens[mask].mean() if mask.sum()>=10 else np.nan)
def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
def test(c,p1,p2):
    a=np.array(store[c][p1]); b=np.array(store[c][p2]); m=np.isfinite(a)&np.isfinite(b); a,b=a[m],b[m]
    if len(a)<10 or np.allclose(a,b): return np.nan,1.0
    return np.mean(a-b), wilcoxon(a-b).pvalue
# peak-valley with FDR across all cats
pv=[(c,)+test(c,"peak","valley") for c in ALL]; q_pv=bh([x[2] for x in pv])
PVQ={c:q for (c,_,_),q in zip(pv,q_pv)}
# ascending-descending with FDR
ad=[(c,)+test(c,"ascending","descending") for c in ALL]; q_ad=bh([x[2] for x in ad])
ADQ={c:q for (c,_,_),q in zip(ad,q_ad)}

print("=== ALL taxonomy categories x phases — mean density per phase, PEAK−VALLEY test ===")
print("   home = phase with highest mean | PV Δ=peak−valley (q FDR) | * q<.05\n")
for tx,cs in TAX.items():
    print(f"-- {tx} --")
    for c in cs:
        means={p:np.nanmean(store[c][p]) for p in ["valley","ascending","descending","peak"]}
        home=max(means,key=means.get)
        a=np.array(store[c]["peak"]); b=np.array(store[c]["valley"]); m=np.isfinite(a)&np.isfinite(b)
        dv=np.nanmean(a[m]-b[m]) if m.sum()>=10 else np.nan
        q=PVQ[c]; star="*" if q<.05 else ""
        arrow="PEAK" if dv>0 else "VALLEY"
        print(f"   {c:11} val={means['valley']:.2f} asc={means['ascending']:.2f} desc={means['descending']:.2f} pk={means['peak']:.2f} | home={home:10} | PVΔ={dv:+.3f}{star} -> {arrow if q<.05 else 'ns'}")
# ascending vs descending summary
nad=sum(1 for c in ALL if ADQ[c]<.05)
print(f"\n=== ASCENDING vs DESCENDING: {nad}/{len(ALL)} categories significant after FDR ===")
if nad:
    for c in ALL:
        if ADQ[c]<.05:
            d=test(c,'ascending','descending')[0]; print(f"   {c}: Δ(asc−desc)={d:+.3f} q={ADQ[c]:.3f}")
else:
    print("   (none — confirms 90s content cannot separate ascending from descending; resolution-limited)")
print(f"\nPEAK vs VALLEY: {sum(1 for c in ALL if PVQ[c]<.05)}/{len(ALL)} categories significant (FDR).")
