"""Paper figure — Study 5: over 26 weeks teams CONSOLIDATE (entropy↓, centralization↑, dominance↑,
semantic recurrence↑). Kendall-tau (Mann-Kendall) trends, two teams."""
import numpy as np,pandas as pd,os
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
import paper_style as ps
ps.setup()
P=pd.read_csv(os.path.expanduser("~/lsh-work/longitudinal_panel.csv"))
PAN=[("mean_entropy","Team-state entropy","↓ less moment-to-moment reorganization"),
     ("net_central","Network centralization","↑ floor centralizes (toward F1)"),
     ("eig_central","Leader eigenvector-centrality","↑ one hub dominates turn-transitions"),
     ("part_entropy","Participation entropy","↓ fewer voices share the floor")]
fig,axes=plt.subplots(2,2,figsize=(11,8))
for ax,(col,name,gloss) in zip(axes.ravel(),PAN):
    taus=[]
    for team,g in P.groupby("team"):
        g=g.sort_values("week")
        ax.plot(g.week,g[col],"o-",color=ps.TEAM[team],ms=3.5,lw=1,alpha=.8,label=team.replace("startup_","team "))
        z=np.polyfit(g.week,g[col],1); ax.plot(g.week,np.polyval(z,g.week),"--",color=ps.TEAM[team],lw=2)
        t,p=kendalltau(g.week,g[col]); taus.append((team,t,p))
    tp,pp=kendalltau(P.week,P[col])
    ax.set_title(f"{name}",loc="left",fontsize=10.5)
    ax.set_xlabel("week"); ax.set_ylabel(name,fontsize=8.5)
    txt="\n".join([f"team {tm[-1].upper()}: τ={t:+.2f} {ps.stars(p)}" for tm,t,p in taus])
    loc="upper right" if col in("mean_entropy","part_entropy") else "lower right"
    ps.statbox(ax,f"{gloss}\npooled τ={tp:+.2f} {ps.stars(pp)}\n{txt}",loc=loc,fontsize=7.4)
axes.ravel()[0].legend(loc="lower left",fontsize=8)
fig.suptitle("Study 5 — Teams consolidate over 26 weeks (replicated across two teams, three lenses)",
             fontsize=12,fontweight="bold",x=.01,ha="left")
ps.caption(fig,"Figure 5. Across ~17 weekly meetings per team, dynamics (team-state entropy ↓) and floor "
  "structure (network centralization ↑, leader eigenvector-centrality ↑, participation entropy ↓) all move "
  "toward a fixed, leader-centric operating point with less moment-to-moment reorganization — "
  "consolidation/routinization, replicated across both teams. Trends are Mann-Kendall (Kendall τ), pooled "
  "and per team; dashed = OLS fit; *p<.05, **p<.01, ***p<.001. Unit of inference = meeting (n = 34).",y=-0.01)
fig.tight_layout(rect=[0,0.03,1,.97])
ps.save(fig,"fig_paper_S5_development")
