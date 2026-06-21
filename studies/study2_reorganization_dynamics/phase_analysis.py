"""Phase analysis of the reorganization signal: ASCENDING / PEAK / DESCENDING / VALLEY.
Phases from entropy_g (cleanest bidirectional metric): zone by UCL/LCL, else by derivative sign.
  (a) Content: ASCENDING vs DESCENDING category density (what drives INTO vs pulls OUT of reorg),
      and PEAK vs VALLEY; paired Wilcoxon across meetings + BH-FDR.
  (b) Geometry: hysteresis in the entropy-%DET plane (is %DET different up vs down at the same
      entropy?) + clean ascent/descent duration & slope asymmetry (consistent excursion boundaries).
NOTE: content is at 90s resolution while phases are ~1s -> ascending/descending content is diluted
within a 90s window; treat content results as EXPLORATORY. Geometry is per-second, no such issue."""
import glob,os,re,json,numpy as np,pandas as pd
from scipy.signal import find_peaks
from scipy.stats import wilcoxon
GM="data/metrics_gorman_l8"; COD2="data/codebooks2"; COD1="data/codebooks"
def load_cod(folder,suf):
    d={}
    for f in glob.glob(f"{folder}/*_{suf}.json"):
        mid=os.path.basename(f).replace(f"_{suf}.json","")
        d[mid]={int(w["t"]):w for w in json.load(open(f))["windows"]}
    return d
c2=load_cod(COD2,"passA"); c1=load_cod(COD1,"passA")
# theoretically key categories (limit multiple comparisons)
DESTAB=["differ","arguable","disagree","bdisagree","explor","delim","bgiveopin"]   # candidate drivers-in
RESOLVE=["converge","bagree","nonarg","feedback","baskinfo","cumul","bsolid"]       # candidate pullers-out
CATS=DESTAB+RESOLVE
CATSRC={c:(c2 if c in ["differ","arguable","disagree","bdisagree","explor","delim","bgiveopin","converge","bagree","nonarg","baskinfo","cumul","bsolid"] else c1) for c in CATS}
CATSRC["feedback"]=c1

def phases(s):
    m,sd=np.nanmean(s),np.nanstd(s); d=np.gradient(s)
    lab=np.full(len(s),"",dtype=object)
    for i,v in enumerate(s):
        if v>m+0.8*sd: lab[i]="peak"
        elif v<m-0.8*sd: lab[i]="valley"
        elif d[i]>0: lab[i]="ascending"
        else: lab[i]="descending"
    return lab

# ---- collect per-meeting phase content + geometry ----
content={c:{"asc":[], "desc":[], "peak":[], "valley":[]} for c in CATS}
hyst=[]; asym=[]
prev={"ascending":0,"peak":0,"descending":0,"valley":0}; nmt=0
for f in sorted(glob.glob(GM+"/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    if mid not in c2: continue
    g=pd.read_csv(f); ent=g.entropy_g.to_numpy(float); det=g.det_g.to_numpy(float); sec=g["second"].to_numpy()
    lab=phases(ent); nmt+=1
    for k in prev: prev[k]+=np.mean(lab==k)
    win=lambda s:int(s//90*90)
    # content per phase
    for c in CATS:
        cd=CATSRC[c].get(mid,{})
        dens=np.array([cd.get(win(s),{}).get(c,0) for s in sec],float)
        for ph,key in [("ascending","asc"),("descending","desc"),("peak","peak"),("valley","valley")]:
            mask=lab==ph
            if mask.sum()>=10: content[c][key].append(dens[mask].mean())
            else: content[c][key].append(np.nan)
    # geometry (a) hysteresis: %DET up vs down at same entropy decile
    bins=np.quantile(ent,np.linspace(0,1,11)); diffs=[]
    asc=(np.gradient(ent)>0); dsc=~asc
    for b in range(10):
        m=(ent>=bins[b])&(ent<bins[b+1])
        if (m&asc).sum()>=20 and (m&dsc).sum()>=20:
            diffs.append(det[m&dsc].mean()-det[m&asc].mean())
    if diffs: hyst.append(np.mean(diffs))
    # geometry (b) clean ascent/descent asymmetry via entropy extrema
    sd=np.nanstd(ent)
    pk,_=find_peaks(ent,prominence=0.5*sd); vl,_=find_peaks(-ent,prominence=0.5*sd)
    ext=sorted([(i,"p") for i in pk]+[(i,"v") for i in vl])
    asc_d=[]; desc_d=[]
    for (i1,t1),(i2,t2) in zip(ext,ext[1:]):
        dur=sec[i2]-sec[i1]
        if dur<=0: continue
        if t1=="v" and t2=="p": asc_d.append(dur)
        elif t1=="p" and t2=="v": desc_d.append(dur)
    if asc_d and desc_d: asym.append((np.median(asc_d),np.median(desc_d)))

print(f"=== Phase prevalence (mean % of seconds, {nmt} meetings) ===")
for k,v in prev.items(): print(f"   {k:11}: {100*v/nmt:.0f}%")

def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
def paired(key1,key2):
    rows=[]
    ps=[]
    for c in CATS:
        a=np.array(content[c][key1]); b=np.array(content[c][key2]); m=np.isfinite(a)&np.isfinite(b)
        a,b=a[m],b[m]
        if len(a)<10 or np.allclose(a,b): rows.append((c,np.nan,1)); ps.append(1); continue
        d=a-b; p=wilcoxon(d).pvalue; rows.append((c,np.mean(d),p)); ps.append(p)
    q=bh(ps)
    return [(c,mn,p,qq) for (c,mn,p),qq in zip(rows,q)]

print("\n=== CONTENT: ASCENDING − DESCENDING (what drives INTO reorganization) [EXPLORATORY] ===")
print("   (+ = more in ascending; sorted; * q<.05)")
for c,mn,p,q in sorted(paired("asc","desc"),key=lambda x:-(x[1] if np.isfinite(x[1]) else -9)):
    fam="destab" if c in DESTAB else "resolve"
    print(f"   {c:11} ({fam}) Δ={mn:+.3f}  q={q:.3f}{'*' if q<.05 else ''}")
print("\n=== CONTENT: PEAK − VALLEY ===")
for c,mn,p,q in sorted(paired("peak","valley"),key=lambda x:-(x[1] if np.isfinite(x[1]) else -9)):
    fam="destab" if c in DESTAB else "resolve"
    print(f"   {c:11} ({fam}) Δ={mn:+.3f}  q={q:.3f}{'*' if q<.05 else ''}")

print("\n=== GEOMETRY ===")
h=np.array(hyst)
try: hp=wilcoxon(h).pvalue
except: hp=1
print(f" Hysteresis (%DET[descending]−%DET[ascending] at same entropy): mean={h.mean():+.2f}  "
      f"{np.mean(h>0)*100:.0f}% mtgs>0  p={hp:.3f}")
A=np.array(asym)
print(f" Ascent vs descent duration (median s/excursion, n={len(A)} mtgs): "
      f"ascent={np.median(A[:,0]):.0f}s  descent={np.median(A[:,1]):.0f}s")
try: ap=wilcoxon(A[:,0],A[:,1]).pvalue
except: ap=1
print(f"   paired Wilcoxon ascent vs descent duration: p={ap:.3f}  "
      f"({'asymmetric' if ap<.05 else 'symmetric — no clean asymmetry'})")
pd.DataFrame(A,columns=["ascent_s","descent_s"]).to_csv("phase_asymmetry.csv",index=False)
