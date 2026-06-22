"""Paper figure — Study 7: anatomy of a reorganization event.
A) ~1/3 transition + ~2/3 interior; B) trigger sets DEPTH not existence; C) developmentally the baseline
falls but the excursion is invariant."""
import numpy as np,pandas as pd,os
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
import paper_style as ps
ps.setup()
L=os.path.expanduser("~/lsh-work")
dec=pd.read_csv(f"{L}/reorg_decomposition_union_W30.csv")
sig=pd.read_csv(f"{L}/reorg_signature.csv")
dep=pd.read_csv(f"{L}/reorg_depth_longitudinal_panel.csv")
fig=plt.figure(figsize=(14,5.2))
gs=fig.add_gridspec(1,3,width_ratios=[0.7,1,1.05],wspace=.34)

# --- A: decomposition (mean across meetings) ---
axA=fig.add_subplot(gs[0,0])
tr=dec.pct_tr.mean(); it=dec.pct_int.mean()
axA.bar([0],[tr],width=.55,color=ps.NEUTRAL,label="transition-driven",zorder=3)
axA.bar([0],[it],bottom=[tr],width=.55,color=ps.COORD,label="endogenous interior",zorder=3)
axA.text(0,tr/2,f"{tr:.0f}%\ntransition",ha="center",va="center",color="white",fontsize=9.5,fontweight="bold")
axA.text(0,tr+it/2,f"{it:.0f}%\ninterior",ha="center",va="center",color="white",fontsize=9.5,fontweight="bold")
axA.set_xticks([]); axA.set_ylim(0,100); axA.set_ylabel("% of reorganization events")
axA.set_title("A  Where it comes from",loc="left",fontsize=10.5)
ps.statbox(axA,"±30 s of a topic/agenda\nboundary vs interior;\nattributable-fraction\nsplit. n=34.",loc="upper right",fontsize=7.2)

# --- B: trigger -> depth ---
axB=fig.add_subplot(gs[0,1])
order=["TRANSITION","INT_HANDOFF","INT_OTHER"]; nice=["topic/agenda\ntransition","interior\nhandoff","interior\nother"]
m=sig.groupby("cls").agg(ent=("entropy","mean"),det=("det","mean")).reindex(order)
x=np.arange(3)
axB.bar(x,m.ent,width=.6,color=[ps.DELIB,ps.COORD,"#b9c2cc"],zorder=3)
for xi,v in zip(x,m.ent): axB.text(xi,v+0.4,f"{v:.1f}",ha="center",fontsize=9)
axB.set_xticks(x); axB.set_xticklabels(nice,fontsize=8.5); axB.set_ylabel("entropy at event (depth)")
axB.set_ylim(0,max(m.ent)*1.18); axB.set_title("B  Trigger sets depth, not existence",loc="left",fontsize=10.5)
ps.statbox(axB,"RMSE spike height EQUAL across\ntriggers (transition vs handoff p=.44);\n"
              "but depth differs — entropy Kruskal–\nWallis p<1e-7, %DET p<1e-7. n=909 events.",loc="upper right",fontsize=7.2)

# --- C: developmental baseline vs excursion ---
axC=fig.add_subplot(gs[0,2])
for team,g in dep.groupby("team"):
    g=g.sort_values("week")
    axC.plot(g.week,g.base_ent,"o-",color=ps.TEAM[team],ms=3,lw=.9,alpha=.45)
    axC.plot(g.week,g.base_ent+g.BORDER_ent_exc,"^--",color=ps.TEAM[team],ms=3,lw=.9,alpha=.9)
    zb=np.polyfit(g.week,g.base_ent,1); axC.plot(g.week,np.polyval(zb,g.week),"-",color=ps.TEAM[team],lw=2.4)
tb,pb=kendalltau(dep.week,dep.base_ent); te,pe=kendalltau(dep.dropna(subset=["BORDER_ent_exc"]).week,dep.dropna(subset=["BORDER_ent_exc"]).BORDER_ent_exc)
axC.plot([],[],"o-",color=ps.INK,label="baseline (resting)")
axC.plot([],[],"^--",color=ps.INK,label="at border events")
axC.set_xlabel("week"); axC.set_ylabel("team-state entropy")
axC.set_title("C  Baseline falls, excursion stays",loc="left",fontsize=10.5)
axC.legend(loc="upper right",fontsize=7.8)
ps.statbox(axC,f"baseline entropy ↓ τ={tb:+.2f} {ps.stars(pb)}\n"
              f"above-baseline excursion flat τ={te:+.2f} {ps.stars(pe)}\n"
              "→ a fixed-size excursion on a sinking baseline.",loc="lower left",fontsize=7.2)

fig.suptitle("Study 7 — Anatomy of a reorganization event: a redistribution of the speaking floor (F1→F2)",
             fontsize=12.5,fontweight="bold",x=.01,ha="left")
ps.caption(fig,"Figure 7. A reorganization event is a redistribution of the speaking floor. (A) ~1/3 is locked to "
  "topic/agenda transitions, ~2/3 is endogenous (handoffs/openings mid-topic). (B) The trigger does not "
  "determine whether a reorganization occurs (equal RMSE-prediction-error spike) but sets its depth. "
  "(C) Over 26 weeks the resting baseline entropy falls (consolidation) while the reorganization's "
  "above-baseline excursion is invariant — a stereotyped event riding a sinking baseline.",y=-0.04)
ps.save(fig,"fig_paper_S7_anatomy")
