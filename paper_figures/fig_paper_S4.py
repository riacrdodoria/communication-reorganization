"""Paper figure — Study 4: reorganization in conversational-floor terms (Edelsky F1↔F2).
Per-meeting within-meeting Pearson r between each floor measure and %DET (recurrence/stability);
Wilcoxon across 34 meetings. Floor-concentration measures rise with %DET (F1 at stable stretches);
the floor equalizes and de-centralizes at reorganization (low %DET → F2)."""
import numpy as np,pandas as pd,os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr,wilcoxon
import paper_style as ps
ps.setup()
F=pd.read_csv(os.path.expanduser("~/lsh-work/floor_windows.csv"))
MEAS=[("top_share","Top-speaker share","concentration"),
      ("net_central","Network centralization","concentration"),
      ("eig_central","Eigenvector centrality","concentration"),
      ("gini_words","Participation Gini (words)","concentration"),
      ("inout_asym","In–out influence asymmetry","concentration"),
      ("turnlen_disp","Turn-length dispersion (F1>F2)","concentration"),
      ("n_active","Active speakers / window","breadth"),
      ("part_entropy","Participation entropy*","breadth")]
rows=[]
for col,name,fam in MEAS:
    rs=[]
    for mid,g in F.groupby("mid"):
        gg=g.dropna(subset=[col,"det_g"])
        if len(gg)<8 or gg[col].std()==0: continue
        rs.append(pearsonr(gg[col],gg.det_g)[0])
    rs=[r for r in rs if np.isfinite(r)]
    p=wilcoxon(rs).pvalue
    rows.append(dict(name=name,fam=fam,r=np.mean(rs),n=len(rs),p=p))
d=pd.DataFrame(rows).sort_values("r")
y=np.arange(len(d))
col=[ps.COORD if f=="concentration" else ps.DELIB for f in d.fam]
fig,ax=plt.subplots(figsize=(9,6.2))
ax.hlines(y,0,d.r,color=col,lw=3,zorder=2)
ax.scatter(d.r,y,color=col,s=70,zorder=3,edgecolor="white",lw=1)
for yi,(_,r) in zip(y,d.iterrows()):
    off=.012 if r.r>=0 else -.012; ha="left" if r.r>=0 else "right"
    ax.text(r.r+off,yi,f"{r['name']}  r={r.r:+.2f} {ps.stars(r.p)}",va="center",ha=ha,fontsize=9,color=ps.INK)
ax.axvline(0,color=ps.INK,lw=.9); ax.set_yticks([]); ax.set_xlim(-.62,.92)
ax.set_xlabel("within-meeting correlation with %DET  (recurrence / floor stability)")
ax.set_title("Study 4 — Reorganization is the floor opening (Edelsky F1 → F2)",loc="left")
# headers in empty quadrants: concentration top-LEFT (negative x, high y), breadth right-MIDDLE
ax.text(-.40,len(d)-1.0,"floor CONCENTRATION\nhigh when stable (F1);\ndrops at reorganization",
        color=ps.COORD,fontsize=9,ha="center",va="center",fontweight="bold",linespacing=1.3)
ax.text(.52,1.4,"floor BREADTH\nrises at\nreorganization (F2)",color=ps.DELIB,fontsize=9,
        ha="center",va="center",fontweight="bold",linespacing=1.3)
ps.statbox(ax,"Test  within-meeting Pearson r of each floor\nmeasure with %DET, then Wilcoxon signed-rank\n"
              "across meetings (n=34). 90 s windows.\n*participation entropy ≈ the state entropy\n"
              "(tautological sanity check), not independent.\nAll effects strengthen at 300 s / between meetings.",loc="lower right")
ps.caption(fig,"Figure 4. Casting the reorganization metrics in the vocabulary of the conversational floor "
  "(Edelsky 1981): measures of floor concentration — one dominant, central speaker (F1) — correlate "
  "positively with %DET (stable stretches), while floor breadth rises as %DET falls. Reorganization is the "
  "floor equalizing and de-centralizing (F1→F2). Bars = mean within-meeting r with %DET; *p<.05, **p<.01, "
  "***p<.001 (Wilcoxon, n=34).",y=-0.03)
fig.tight_layout(rect=[0,0.02,1,1])
ps.save(fig,"fig_paper_S4_floor_dynamics")
