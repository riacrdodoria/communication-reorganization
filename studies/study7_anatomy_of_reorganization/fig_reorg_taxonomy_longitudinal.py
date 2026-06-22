"""Figure: the CONTENT (taxonomy) of reorganization is developmentally stable.
A: continuous content-axis corr(rmse, coordination-deliberation composite) over weeks, both teams (flat).
B: per-taxonomy reorganization content-axis, early vs late halves (no shift)."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
P=pd.read_csv("reorg_taxonomy_longitudinal_panel.csv")
P["half"]=np.where(P.week<P.groupby('team').week.transform('median'),"early","late")
COL={"startup_a":"#2E7D8C","startup_b":"#d95f02"}
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5))
for team,g in P.groupby("team"):
    g=g.sort_values("week")
    ax1.plot(g.week,g.axis_cont,"o-",color=COL[team],ms=4,lw=1.1,alpha=.85,label=team)
    z=np.polyfit(g.week,g.axis_cont,1); ax1.plot(g.week,np.polyval(z,g.week),"--",color=COL[team],lw=1.6)
    t,p=kendalltau(g.week,g.axis_cont)
    ax1.text(.02,.12 if team=="startup_a" else .05,f"{team}: τ={t:+.2f} (p={p:.2f})",
             transform=ax1.transAxes,color=COL[team],fontsize=8.5)
ax1.axhline(0,color="#bbb",lw=.8)
ax1.set_xlabel("week (within team)"); ax1.set_ylabel("content-axis  corr(rmse, coordination−deliberation)")
ax1.set_title("A  Continuous content of reorganization over time\nstays coordination-flavored; no trend (FDR 0/11)",fontsize=10.5,loc="left")
ax1.legend(fontsize=8.5,loc="upper right")

TAXES=["CACS","IAM","Mercer","Bales","act4teams","ISO"]
early=[P[P.half=="early"][f"axis_{t}"].mean() for t in TAXES]
late=[P[P.half=="late"][f"axis_{t}"].mean() for t in TAXES]
x=np.arange(len(TAXES)); w=.38
ax2.bar(x-w/2,early,w,label="early weeks",color="#7aa6b0")
ax2.bar(x+w/2,late,w,label="late weeks",color="#9aa0a6")
ax2.axhline(0,color="#888",lw=.8); ax2.set_xticks(x); ax2.set_xticklabels(TAXES,fontsize=9)
ax2.set_ylabel("reorganization content-axis (event lift, SD)")
ax2.set_title("B  Per-taxonomy content of reorganization\nearly vs late — no taxonomy shifts",fontsize=10.5,loc="left")
ax2.legend(fontsize=8.5)
fig.suptitle("The WHAT of reorganization (taxonomy content) is developmentally invariant — like the WHERE",fontsize=11.5,y=1.0)
fig.tight_layout(); fig.savefig("fig_reorg_taxonomy_longitudinal.png",dpi=150)
print("wrote fig_reorg_taxonomy_longitudinal.png")
