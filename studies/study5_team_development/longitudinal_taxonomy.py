"""Longitudinal evolution of the taxonomy content over the 26 weeks (per team).
Per meeting = mean category density across its 90s windows. Mann-Kendall trend per team per category
(grouped by taxonomy), + a deliberation<->coordination composite trajectory. Does content shift as the
floor consolidates (entropy down)? Output: longitudinal_taxonomy_panel.csv, fig_longitudinal_taxonomy.png."""
import glob,os,re,json,numpy as np,pandas as pd
from datetime import date
from scipy.stats import kendalltau
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
COD2="data/codebooks2"; COD1="data/codebooks"
def parse(mid):
    m=re.match(r"(\d{4})\.(\d{2})\.(\d{2})(.+)",mid); y,mo,d,t=m.groups(); return t,date(int(y),int(mo),int(d))
TAX={
"CACS":["arguable","converge","disagree","delim","nonarg"],
"Bales":["bgiveinfo","bgiveopin","bgivesug","baskinfo","baskopin","basksug","bsolid","btension","bagree","bdisagree","btensh","bantag"],
"ISO":["qset","qprop","directive","commissive","feedback"],
"act4teams":["proact","struct","coop","cprod","ginfo","ktrans","namep","names","linkp","links","linkc"],
"IAM":["iam1","iam2","iam3","iam4","iam5"],
"Mercer":["disput","cumul","explor"]}
CAT2TAX={c:t for t,cs in TAX.items() for c in cs}
COORD=["nonarg","converge","baskinfo","bagree","bsolid","feedback","qprop","qset","directive","commissive","struct","coop","ginfo","iam5"]
DELIB=["arguable","delim","bgiveopin","explor","ktrans","iam1","iam3","iam4","linkp","linkc","namep","names","links"]
def load(folder,suf):
    d={}
    for f in glob.glob(f"{folder}/*_{suf}.json"):
        mid=os.path.basename(f).replace(f"_{suf}.json","")
        d[mid]=json.load(open(f))["windows"]
    return d
c2=load(COD2,"passA"); c1=load(COD1,"passA")
ALLCATS=[c for cs in TAX.values() for c in cs]
rows=[]
for mid in sorted(set(c2)|set(c1)):
    team,dt=parse(mid); r=dict(mid=mid,team=team,dt=dt)
    for src in (c2.get(mid,[]),c1.get(mid,[])):
        if not src: continue
        df=pd.DataFrame(src)
        for c in ALLCATS:
            if c in df.columns: r[c]=df[c].mean()
    rows.append(r)
P=pd.DataFrame(rows)
P["dt"]=pd.to_datetime(P["dt"])
P=P.sort_values(["team","dt"]).reset_index(drop=True)
P["week"]=P.groupby("team").cumcount()+1
# z-score each category across meetings for composites
present=[c for c in ALLCATS if c in P.columns]
Z=P[present].apply(lambda s:(s-s.mean())/s.std(ddof=0))
P["coord_comp"]=Z[[c for c in COORD if c in Z.columns]].mean(1)
P["delib_comp"]=Z[[c for c in DELIB if c in Z.columns]].mean(1)
P["balance"]=P["coord_comp"]-P["delib_comp"]   # + = coordination-heavy
P.to_csv("longitudinal_taxonomy_panel.csv",index=False)

print("=== Per-category Mann-Kendall trend over 26 weeks (Kendall tau per team; * p<.05) ===")
print("    grouped by taxonomy; flag = both teams same direction\n")
def tau(sub,c):
    s=sub.dropna(subset=[c]);
    if len(s)<8: return (np.nan,1)
    return kendalltau(s["week"],s[c])
repl=[]
for tx,cs in TAX.items():
    print(f"-- {tx} --")
    for c in cs:
        if c not in P.columns: continue
        a=tau(P[P.team=="startup_a"],c); b=tau(P[P.team=="startup_b"],c)
        same = np.sign(a[0])==np.sign(b[0]) and not np.isnan(a[0]) and not np.isnan(b[0])
        flag = "  <<both "+("UP" if a[0]>0 else "DOWN")+(" & sig" if (a[1]<.05 and b[1]<.05) else "") if same else ""
        if same and (a[1]<.1 or b[1]<.1): repl.append((c,tx,a[0],b[0],a[1],b[1]))
        print(f"   {c:11} a:tau={a[0]:+.2f}{'*' if a[1]<.05 else ' '}  b:tau={b[0]:+.2f}{'*' if b[1]<.05 else ' '}{flag}")
print("\n=== Replicated category trends (both same dir, >=1 team p<.1) ===")
for c,tx,ta,tb,pa,pb in sorted(repl,key=lambda x:-(abs(x[2])+abs(x[3]))/2):
    d="UP" if ta>0 else "DOWN"
    print(f"   {c:11} ({tx:9}) {d:4}  a={ta:+.2f}{'*' if pa<.05 else ''} b={tb:+.2f}{'*' if pb<.05 else ''}")
print("\n=== Deliberation<->coordination BALANCE trend (composite) ===")
for tm in ["startup_a","startup_b"]:
    sub=P[P.team==tm]
    for comp in ["coord_comp","delib_comp","balance"]:
        t,p=kendalltau(sub["week"],sub[comp])
        print(f"   {tm} {comp:11}: tau={t:+.2f}{'*' if p<.05 else ''}")

# figure: balance + a few replicated categories
fig,axes=plt.subplots(2,2,figsize=(13,8)); axes=axes.ravel()
col={"startup_a":"#2E7D8C","startup_b":"#d95f02"}
panels=[("balance","Coordination − Deliberation balance"),("coord_comp","Coordination composite"),
        ("delib_comp","Deliberation composite")]
# pick top replicated category for 4th panel
topcat=repl[0][0] if repl else "arguable"
panels.append((topcat,f"{topcat} ({CAT2TAX.get(topcat,'')})"))
for ax,(v,lab) in zip(axes,panels):
    for tm,sub in P.groupby("team"):
        sub=sub.sort_values("week"); ax.plot(sub["week"],sub[v],"o-",color=col[tm],ms=4,lw=1.4,label=tm,alpha=.85)
    ax.axvline(10.5,color="#888",ls="--",lw=1); ax.axhline(0,color="#ccc",lw=.6)
    ax.set_title(lab,fontsize=11); ax.set_xlabel("meeting (week)",fontsize=8); ax.tick_params(labelsize=7)
axes[0].legend(fontsize=8)
fig.suptitle("Longitudinal evolution of taxonomy content (2 teams × 17 weekly meetings)",fontsize=13)
plt.tight_layout(rect=[0,0,1,0.97]); plt.savefig("fig_longitudinal_taxonomy.png",dpi=170,bbox_inches="tight")
print("\nsaved longitudinal_taxonomy_panel.csv, fig_longitudinal_taxonomy.png")
