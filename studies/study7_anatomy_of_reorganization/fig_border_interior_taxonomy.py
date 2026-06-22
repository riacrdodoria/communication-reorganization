"""Does each taxonomy category predict the BORDER and the INTERIOR perturbation the same way?
Scatter: x = lift at border peaks, y = lift at interior peaks. On-diagonal = same signature; both>0 =
coordination content, both<0 = deliberation content. Color by taxonomy; filled = sig in at least one."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
M=pd.read_csv("reorg_taxonomy_borderinterior.csv")
COL={"CACS":"#2E7D8C","IAM":"#d95f02","Mercer":"#7570b3","Bales":"#e7298a","act4teams":"#66a61e","ISO":"#e6ab02"}
fig,ax=plt.subplots(figsize=(9.2,8.2))
lim=1.0
ax.axhline(0,color="#bbb",lw=.8); ax.axvline(0,color="#bbb",lw=.8)
ax.plot([-lim,lim],[-lim,lim],"--",color="#999",lw=.8,zorder=1)
for _,r in M.iterrows():
    if pd.isna(r.border_lift) or pd.isna(r.int_lift): continue
    sig=(str(r.border_sig)!="nan" and r.border_sig) or (str(r.int_sig)!="nan" and r.int_sig)
    ax.scatter(r.border_lift,r.int_lift,s=70 if sig else 32,c=COL[r.tax],
               edgecolor="k" if sig else "none",lw=.6,alpha=.9,zorder=3)
# annotate notable ones
NOTE={"non-arguable","exploratory","arguable","gives opinion","feedback","prop-question","asks info",
      "knowledge transfer","structuring","directive","set-question","names problem","negotiation","agrees"}
for _,r in M.iterrows():
    if r.label in NOTE and pd.notna(r.border_lift):
        ax.annotate(f"{r.tax[:4]}:{r.label}",(r.border_lift,r.int_lift),fontsize=7,
                    xytext=(4,3),textcoords="offset points",color="#333")
ax.set_xlim(-.7,1.05); ax.set_ylim(-.45,.75)
ax.set_xlabel("lift at BORDER perturbation (topic/agenda transition)",fontsize=11)
ax.set_ylabel("lift at INTERIOR perturbation (endogenous floor turnover)",fontsize=11)
ax.text(.7,.68,"COORDINATION content\n(↑ both perturbations)",ha="center",fontsize=9,color="#2a7",fontweight="bold")
ax.text(-.45,-.38,"DELIBERATION content\n(↓ both perturbations)",ha="center",fontsize=9,color="#b52",fontweight="bold")
ax.text(.0,.72,"points hug the diagonal → both perturbations share one content signature;\n"
        "border lifts are larger (x-spread > y-spread) → the boundary reorganization is deeper",
        ha="center",fontsize=8,fontstyle="italic",color="#555")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc=COL[t],label=t) for t in COL],fontsize=8.5,loc="lower right",title="taxonomy")
ax.set_title("Each taxonomy predicts BOTH perturbations the same way — both are coordination\n"
             "(border 25/40 sig, interior 22/40; border deeper; a few border- vs interior-specific moves)",
             fontsize=10.5)
fig.tight_layout(); fig.savefig("fig_border_interior_taxonomy.png",dpi=150)
print("wrote fig_border_interior_taxonomy.png")
