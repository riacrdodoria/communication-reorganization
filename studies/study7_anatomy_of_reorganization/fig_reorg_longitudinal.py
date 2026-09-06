"""Figure: border share of reorganization over the ~26 weeks, per team, with the interior reorg rate.
Shows the split is developmentally STABLE (~1/3 border) and the two teams diverge weakly."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
P=pd.read_csv("reorg_longitudinal_panel.csv")
COL={"startup_a":"#2E7D8C","startup_b":"#d95f02"}
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5))
for team,g in P.groupby("team"):
    g=g.sort_values("week")
    ax1.plot(g.week,g.border_share,"o-",color=COL[team],ms=4,lw=1.2,alpha=.85,label=f"{team}")
    z=np.polyfit(g.week,g.border_share,1); ax1.plot(g.week,np.polyval(z,g.week),"--",color=COL[team],lw=1.6)
    t,p=kendalltau(g.week,g.border_share)
    ax1.text(.02,.06 if team=="startup_b" else .12,f"{team}: τ={t:+.2f} (p={p:.2f})",
             transform=ax1.transAxes,color=COL[team],fontsize=8.5)
ax1.axhline(P.border_share.mean(),color="#999",ls=":",lw=1)
ax1.text(P.week.max(),P.border_share.mean()+1.5,f"pooled mean {P.border_share.mean():.0f}%",
         color="#666",fontsize=8,ha="right")
ax1.set_xlabel("week (within team)"); ax1.set_ylabel("BORDER share of reorganization (%)")
ax1.set_title("A  Border share is developmentally stable (~⅓)\nno significant trend; teams diverge weakly",fontsize=10.5,loc="left")
ax1.set_ylim(0,75); ax1.legend(fontsize=8.5,loc="upper right")

for team,g in P.groupby("team"):
    g=g.sort_values("week")
    ax2.plot(g.week,g.r_int,"o-",color=COL[team],ms=4,lw=1.2,alpha=.85,label=team)
    z=np.polyfit(g.week,g.r_int,1); ax2.plot(g.week,np.polyval(z,g.week),"--",color=COL[team],lw=1.6)
    t,p=kendalltau(g.week,g.r_int)
    ax2.text(.02,.06 if team=="startup_b" else .12,f"{team}: τ={t:+.2f} (p={p:.2f})",
             transform=ax2.transAxes,color=COL[team],fontsize=8.5)
ax2.set_xlabel("week (within team)"); ax2.set_ylabel("INTERIOR reorg-event rate (% of interior seconds)")
ta,pa=kendalltau(P[P.team=="startup_a"].sort_values("week").week,P[P.team=="startup_a"].sort_values("week").r_int)
ax2.set_title("B  Interior reorganization rate over time\n"+(f"startup_a declines (τ={ta:+.2f}, p={pa:.3f})" if pa<.05 else f"no significant trend (startup_a τ={ta:+.2f}, p={pa:.2f})"),fontsize=10.5,loc="left")
ax2.legend(fontsize=8.5,loc="upper right")
fig.suptitle("Over 26 weeks the WHERE of reorganization (border vs interior) stays put — only its rate/depth drifts",fontsize=11.5,y=1.0)
fig.tight_layout(); fig.savefig("fig_reorg_longitudinal.png",dpi=150)
print("wrote fig_reorg_longitudinal.png")
