"""Figure: (A) transition vs interior decomposition of reorganization (union boundaries, W sweep);
(B) what marks INTERIOR reorganization - standardized effect sizes, floor/form vs content."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

TR={15:19.9,30:32.4,45:43.3}; INT={15:80.1,30:67.6,45:56.7}   # union, event-based (from PART A)
R=pd.read_csv("reorg_interior_drivers.csv")
COORD="#2E7D8C"; DELIB="#d95f02"; GREY="#9aa0a6"
fig,(axA,axB)=plt.subplots(1,2,figsize=(14,6),gridspec_kw={"width_ratios":[0.8,1.2]})

# ---- A: stacked decomposition ----
Ws=[15,30,45]; x=np.arange(len(Ws))
tr=[TR[w] for w in Ws]; it=[INT[w] for w in Ws]
axA.bar(x,tr,color="#444",width=0.55,label="transition-driven excess",zorder=3)
axA.bar(x,it,bottom=tr,color=COORD,width=0.55,label="interior / background",zorder=3)
for xi,t in zip(x,tr): axA.text(xi,t/2,f"{t:.0f}%",ha="center",va="center",color="w",fontsize=10,fontweight="bold")
for xi,t,i in zip(x,tr,it): axA.text(xi,t+i/2,f"{i:.0f}%",ha="center",va="center",color="w",fontsize=10,fontweight="bold")
axA.set_xticks(x); axA.set_xticklabels([f"±{w}s" for w in Ws]); axA.set_xlabel("transition-zone half-width")
axA.set_ylabel("% of reorganization events"); axA.set_ylim(0,100)
axA.set_title("A  Transition vs interior\n(union of topic + L10 boundaries; events ~2.7× denser in zones)",
              fontsize=10.5,loc="left")
axA.legend(fontsize=8.5,loc="lower center")

# ---- B: interior drivers ----
order=R.sort_values("d")
FORM={"speaker switches (+/-15s)","turns / 90s","distinct speakers (+/-15s)","speaker-transition entropy",
      "active speakers / 90s","top-speaker share (floor concentration)","network centralization","turn latency"}
y=np.arange(len(order)); col=[GREY if l in FORM else DELIB for l in order.label]
axB.barh(y,order.d,color=col,zorder=3)
for yi,(_,r) in zip(y,order.iterrows()):
    off=0.02 if r.d>=0 else -0.02; ha="left" if r.d>=0 else "right"
    axB.text(r.d+off,yi,f"{r.d:+.2f}{r.sig}",va="center",ha=ha,fontsize=7.6)
axB.axvline(0,color="#333",lw=.8); axB.set_yticks(y); axB.set_yticklabels(order.label,fontsize=8)
axB.set_xlabel("standardized mean difference  (interior reorg − interior baseline)")
axB.set_xlim(-0.75,1.35)
axB.set_title("B  What marks INTERIOR reorganization (the other ⅔)\nfloor/turn-taking form (grey) vs talk content (orange)",
              fontsize=10.5,loc="left")
axB.legend(handles=[Patch(fc=GREY,label="floor / turn-taking form"),Patch(fc=DELIB,label="talk content")],
           fontsize=8.5,loc="lower right")
axB.text(.98,.5,"interior reorg = the floor opening to\nrapid multi-party turn-taking,\nnot argument/deliberation",
         transform=axB.transAxes,ha="right",va="center",fontsize=8,fontstyle="italic",color="#555")

fig.suptitle("Reorganization = part topic/agenda transition (~⅓), part endogenous floor turnover (~⅔)",
             fontsize=12,y=0.99)
fig.tight_layout(rect=[0,0,1,0.96]); fig.savefig("fig_reorg_decomp.png",dpi=150)
print("wrote fig_reorg_decomp.png")
