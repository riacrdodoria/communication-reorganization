"""Longitudinal POC: one summary per meeting -> per-team 17-point trajectories.
Trend (Mann-Kendall via Kendall tau) + mid-Jan->Feb gap (nature UNCERTAIN: summer pause vs uncollected
meetings; NOT interpreted as a perturbation) before/after contrast.
Builds longitudinal_panel.csv and fig_longitudinal.png."""
import glob,os,re,numpy as np,pandas as pd
from datetime import date
from scipy.stats import kendalltau, mannwhitneyu
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
GM="data/metrics_gorman_l8"
def parse(mid):
    m=re.match(r"(\d{4})\.(\d{2})\.(\d{2})(.+)",mid)
    y,mo,d,team=m.groups(); return team,date(int(y),int(mo),int(d))

# reorg-event rate + metric means per meeting
rows=[]
for f in sorted(glob.glob(GM+"/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    g=pd.read_csv(f); team,dt=parse(mid)
    x=g["rmse_g"].to_numpy(float); m,s=np.nanmean(x),np.nanstd(x)
    reorg_rate=100*np.nanmean(x>m+2.33*s)              # % seconds that are RMSE peaks
    rows.append(dict(mid=mid,team=team,dt=dt,
        mean_entropy=g.entropy_g.mean(),mean_det=g.det_g.mean(),mean_rmse=g.rmse_g.mean(),
        reorg_rate=reorg_rate))
P=pd.DataFrame(rows)
# floor (per-meeting mean of window measures)
fw=pd.read_csv("floor_windows.csv").groupby("mid")[["gini_words","top_share","turnlen_disp","part_entropy"]].mean()
net=pd.read_csv("floor_network_meeting.csv").set_index("mid")[["net_central","eig_central"]]
tri=pd.read_csv("triangulation_windows.csv").groupby("mid")[["sem_rec","turn_len","coh"]].mean()
P=P.set_index("mid").join(fw).join(net).join(tri).reset_index()
# week index per team
P["dt"]=pd.to_datetime(P["dt"])
P=P.sort_values(["team","dt"]).reset_index(drop=True)
P["week"]=P.groupby("team").cumcount()+1
P["gap_days"]=P.groupby("team")["dt"].diff().dt.days
P.to_csv("longitudinal_panel.csv",index=False)

VARS=[("mean_entropy","Mean entropy"),("mean_det","Mean %DET"),("reorg_rate","Reorg-event rate (%)"),
      ("top_share","Top-speaker share"),("gini_words","Participation Gini"),("eig_central","Network centrality"),
      ("turnlen_disp","Turn-length disp (F1>F2)"),("sem_rec","Semantic recurrence"),("turn_len","Turn length")]

print("=== Mann-Kendall trend per team (Kendall tau vs week; * p<.05) ===")
print(f"{'variable':24}| {'startup_a':>16} | {'startup_b':>16} | both same dir?")
for v,lab in VARS:
    cells={}
    for tm,sub in P.groupby("team"):
        sub=sub.dropna(subset=[v])
        tau,p=kendalltau(sub["week"],sub[v])
        cells[tm]=(tau,p)
    a,b=cells.get("startup_a",(np.nan,1)),cells.get("startup_b",(np.nan,1))
    same="YES" if (np.sign(a[0])==np.sign(b[0]) and a[1]<.1 and b[1]<.1) else ("dir-agree" if np.sign(a[0])==np.sign(b[0]) else "no")
    sa=f"tau={a[0]:+.2f}{'*' if a[1]<.05 else ''}"; sb=f"tau={b[0]:+.2f}{'*' if b[1]<.05 else ''}"
    print(f"{lab:24}| {sa:>16} | {sb:>16} | {same}")

print("\n=== mid-Jan->Feb gap (nature uncertain): weeks 1-10 vs 11-17, per team ===")
print(f"{'variable':24}| {'a: before->after':>22} | {'b: before->after':>22} | both same dir?")
for v,lab in VARS:
    dirs=[]
    cells={}
    for tm,sub in P.groupby("team"):
        bef=sub[sub.week<=10][v].mean(); aft=sub[sub.week>=11][v].mean()
        cells[tm]=(bef,aft); dirs.append(np.sign(aft-bef))
    same="YES" if dirs[0]==dirs[1] and dirs[0]!=0 else "no"
    ca=f"{cells['startup_a'][0]:.1f}->{cells['startup_a'][1]:.1f}"
    cb=f"{cells['startup_b'][0]:.1f}->{cells['startup_b'][1]:.1f}"
    print(f"{lab:24}| {ca:>22} | {cb:>22} | {same}")

# figure
fig,axes=plt.subplots(3,3,figsize=(15,11)); axes=axes.ravel()
col={"startup_a":"#2E7D8C","startup_b":"#d95f02"}
for ax,(v,lab) in zip(axes,VARS):
    for tm,sub in P.groupby("team"):
        sub=sub.sort_values("week")
        ax.plot(sub["week"],sub[v],"o-",color=col[tm],ms=4,lw=1.4,label=tm,alpha=.85)
    ax.axvline(10.5,color="#888",ls="--",lw=1); ax.text(10.6,ax.get_ylim()[1],"Jan→Feb gap",fontsize=7,color="#888",va="top")
    ax.set_title(lab,fontsize=10); ax.set_xlabel("meeting (week index)",fontsize=8); ax.tick_params(labelsize=7)
axes[0].legend(fontsize=8)
fig.suptitle("Longitudinal trajectories of communication-reorganization & floor measures (2 teams × 17 weekly meetings)",fontsize=13)
plt.tight_layout(rect=[0,0,1,0.98]); plt.savefig("fig_longitudinal.png",dpi=170,bbox_inches="tight")
print("\nsaved longitudinal_panel.csv, fig_longitudinal.png")
