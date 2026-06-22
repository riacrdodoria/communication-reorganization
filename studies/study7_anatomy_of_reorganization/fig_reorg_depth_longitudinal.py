"""Figure: what consolidates is the BASELINE, not the reorganization excursion.
A: per-meeting baseline entropy vs entropy-at-border-events over weeks (parallel decline = constant gap).
B: pooled Kendall tau — baseline & absolute event entropy fall (FDR**), but spike prominence and the
   above-baseline excursion are flat."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
from statsmodels.stats.multitest import multipletests
P=pd.read_csv("reorg_depth_longitudinal_panel.csv")
P["BORDER_ent_abs2"]=P.base_ent+P.BORDER_ent_exc
COL={"startup_a":"#2E7D8C","startup_b":"#d95f02"}
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5.2),gridspec_kw={"width_ratios":[1.1,1]})
for team,g in P.groupby("team"):
    g=g.sort_values("week")
    ax1.plot(g.week,g.base_ent,"o-",color=COL[team],ms=3,lw=1,alpha=.5)
    ax1.plot(g.week,g.BORDER_ent_abs,"^--",color=COL[team],ms=3,lw=1,alpha=.9)
    zb=np.polyfit(g.week,g.base_ent,1); ax1.plot(g.week,np.polyval(zb,g.week),"-",color=COL[team],lw=2.2)
for team in COL: ax1.plot([],[],"-",color=COL[team],lw=2,label=team)
ax1.plot([],[],"o-",color="#555",label="baseline entropy (resting)")
ax1.plot([],[],"^--",color="#555",label="entropy AT border events")
ax1.set_xlabel("week (within team)"); ax1.set_ylabel("team-state entropy")
ax1.set_title("A  Baseline slides down; the event sits a constant gap above it\n"
              "(both lines fall in parallel → the excursion is preserved)",fontsize=10,loc="left")
ax1.legend(fontsize=7.8,loc="upper right",ncol=1)

MEAS=[("base_ent","baseline entropy"),("BORDER_ent_abs","entropy @ border (abs)"),
      ("INTERIOR_ent_abs","entropy @ interior (abs)"),("BORDER_ent_exc","border EXCURSION (vs base)"),
      ("INTERIOR_ent_exc","interior EXCURSION"),("BORDER_peak_z","border spike prominence"),
      ("INTERIOR_peak_z","interior spike prominence")]
taus=[]; ps=[]
for c,_ in MEAS:
    s=P.dropna(subset=[c]); t,p=kendalltau(s.week,s[c]); taus.append(t); ps.append(p)
q=multipletests(ps,method="fdr_bh")[1]
y=np.arange(len(MEAS))[::-1]
cols=["#c0392b" if (taus[i]<0 and q[i]<.05) else "#999" for i in range(len(MEAS))]
ax2.barh(y,taus,color=cols,zorder=3)
for i,(c,lab) in enumerate(MEAS):
    star="**" if q[i]<.01 else "*" if q[i]<.05 else ""
    ax2.text(taus[i]+(0.02 if taus[i]>=0 else -0.02),y[i],f"{taus[i]:+.2f}{star}",
             va="center",ha="left" if taus[i]>=0 else "right",fontsize=8)
ax2.axvline(0,color="#333",lw=.8); ax2.set_yticks(y); ax2.set_yticklabels([m[1] for m in MEAS],fontsize=8.3)
ax2.set_xlim(-0.6,0.4); ax2.set_xlabel("pooled Kendall τ over weeks (red = ↓, FDR-sig)")
ax2.set_title("B  What changes vs what is invariant\nbaseline & absolute fall (FDR**); excursion & prominence flat",fontsize=10,loc="left")
fig.suptitle("Maturation lowers the resting operating point — the reorganization excursion keeps its size",fontsize=11.5,y=1.0)
fig.tight_layout(); fig.savefig("fig_reorg_depth_longitudinal.png",dpi=150)
print("wrote fig_reorg_depth_longitudinal.png")
