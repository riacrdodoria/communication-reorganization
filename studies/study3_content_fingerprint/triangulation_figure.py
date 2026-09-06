"""Figure: coding-free text measures aligned to the reorganization axis, RAW vs CONTROLLED.
reorg_Z = (Z_entropy + Z_rmse - Z_det)/sqrt(3)  (entropy & RMSE up, %DET down = reorganization).
Hollow bars = raw within-meeting Stouffer Z; filled bars = after partialling out turn length and
turns-per-window within meeting (METHODS §7). Reads triangulation_Z.csv written by triangulation_test.py."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
R=pd.read_csv("triangulation_Z.csv")
FAM={"sem_rec":"C","coh":"C","nov":"C","liwc_lsm":"C","lsm_curated":"C","connective":"C","content_overlap":"C",
     "word_entropy":"C","ttr":"C","mtld":"C","hapax":"C","sem_det":"C",
     "turn_len":"S","n_turns":"S","transition_entropy":"S","latency":"S"}
R=R[R.feat.isin(FAM)].copy(); R["fam"]=R.feat.map(FAM)
R=R.sort_values("reorgZ_ctrl")
n_win=len(pd.read_csv("triangulation_windows.csv"))
fig,ax=plt.subplots(figsize=(10.5,9))
col={"C":"#2E7D8C","S":"#9e9e9e"}
y=np.arange(len(R))
ax.barh(y,R.reorgZ_raw,color="white",edgecolor=[col[f] for f in R.fam],lw=1.2,height=0.72,zorder=2)
ax.barh(y,R.reorgZ_ctrl,color=[col[f] for f in R.fam],edgecolor="black",lw=0.4,height=0.45,zorder=3)
ax.set_yticks(y); ax.set_yticklabels(R.label,fontsize=10)
ax.axvline(0,color="black",lw=0.9)
for sv in (1.96,3.29):
    for s in (sv,-sv): ax.axvline(s,color="#bbb",ls=":",lw=0.8)
for i,(_,r) in enumerate(R.iterrows()):
    st='***' if abs(r.reorgZ_ctrl)>3.29 else '**' if abs(r.reorgZ_ctrl)>2.58 else '*' if abs(r.reorgZ_ctrl)>1.96 else 'ns'
    xx=r.reorgZ_raw if abs(r.reorgZ_raw)>abs(r.reorgZ_ctrl) else r.reorgZ_ctrl
    ax.text(xx+(0.6 if xx>0 else -0.6),i,st,va="center",ha="left" if xx>0 else "right",fontsize=8,color="#333")
ax.set_xlabel("← concentrated in STABLE periods      reorganization-aligned Stouffer Z      enriched at REORGANIZATION →",fontsize=10.5)
ax.set_title("Coding-free text measures and communication reorganization: raw vs turn-length-controlled\n"
             f"No human/LLM coding · {n_win} windows · 34 meetings · within-meeting circular null",fontsize=12,pad=10)
ax.text(0.27,1.02,"STABILITY / DELIBERATION",transform=ax.transAxes,ha="center",fontsize=10.5,fontweight="bold",color="#C0504D")
ax.text(0.76,1.02,"REORGANIZATION / COORDINATION",transform=ax.transAxes,ha="center",fontsize=10.5,fontweight="bold",color="#2E7D8C")
leg=[Patch(facecolor=col["C"],label="Content-based measure (filled = after turn-length & turn-count control)"),
     Patch(facecolor="white",edgecolor=col["C"],label="raw (uncontrolled) Z"),
     Patch(facecolor=col["S"],label="Structural (turn-derived — partly mechanical)")]
ax.legend(handles=leg,loc="lower right",fontsize=8.5,frameon=True)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig("fig_triangulation.png",dpi=200,bbox_inches="tight")
print("saved fig_triangulation.png")
print(R[["label","fam","reorgZ_raw","reorgZ_ctrl"]].round(2).to_string(index=False))
