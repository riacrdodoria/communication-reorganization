"""Figure: reorganization across EOS Level 10 agenda stages.
Panel A  - per-stage turn-taking reorganization (entropy + reorg-event rate), agenda order, review vs IDS.
Panel B  - content contrast: taxonomy categories enriched in REVIEW (procedural) vs IDS (deliberation)."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ORDER=["segue","scorecard","rock_review","headlines","todo","ids","conclude"]
NICE={"segue":"Segue","scorecard":"Scorecard","rock_review":"Rock review","headlines":"Headlines",
      "todo":"To-do review","ids":"IDS\n(problem-solving)","conclude":"Conclude"}
REVIEW={"scorecard","rock_review","todo"}
P=pd.read_csv("l10_stage_metrics.csv")
def wmean(g,c): return np.average(g[c],weights=g["secs"])
agg=P.groupby("stage").apply(lambda g:pd.Series({
    "entropy":wmean(g,"entropy"),"det":wmean(g,"det"),"reorg":wmean(g,"reorg_rate"),
    "n":g.mid.nunique()})).reindex(ORDER)

COORD="#2E7D8C"; DELIB="#d95f02"; GREY="#9aa0a6"
def col(st): return COORD if st in REVIEW else (DELIB if st=="ids" else GREY)
cols=[col(s) for s in ORDER]; x=np.arange(len(ORDER))

fig,(axA,axB)=plt.subplots(1,2,figsize=(14,6),gridspec_kw={"width_ratios":[1.05,1]})

# ---- Panel A ----
axA.bar(x,agg["entropy"],color=cols,width=0.62,zorder=3)
for xi,st in zip(x,ORDER):
    axA.text(xi,agg["entropy"][st]+0.4,f"{agg['entropy'][st]:.0f}",ha="center",va="bottom",fontsize=9)
axA.set_xticks(x); axA.set_xticklabels([NICE[s] for s in ORDER],fontsize=8.5)
axA.set_ylabel("Team-state entropy  (reorganization →)",fontsize=10)
axA.set_ylim(0,max(agg["entropy"])*1.18)
ax2=axA.twinx()
ax2.plot(x,agg["reorg"],"-o",color="#222",lw=1.6,ms=5,zorder=4)
ax2.set_ylabel("Reorg-event rate (%)  — line",fontsize=9.5); ax2.set_ylim(0,max(agg["reorg"])*1.5)
axA.set_title("A  Reorganization by L10 stage\nreview 37.6 vs IDS 33.5  Δ=+4.1, p=.001**  ·  "
              "reorg-rate 4.2 vs 2.7  p=.009**",fontsize=10.5,loc="left")
axA.legend(handles=[Patch(fc=COORD,label="Procedural review (coordination)"),
                    Patch(fc=DELIB,label="IDS (deliberation)"),
                    Patch(fc=GREY,label="Other stages")],fontsize=8.5,loc="upper left",framealpha=.9)

# ---- Panel B ----
R=pd.read_csv("l10_taxonomy_review_vs_ids.csv")
top_rev=R[R.delta>0].sort_values("delta",ascending=False).head(3)
top_ids=R[R.delta<0].sort_values("delta").head(8)
B=pd.concat([top_ids[::-1],top_rev])
labels=[f"{r.tax}: {r.label}" for _,r in B.iterrows()]
y=np.arange(len(B)); bcol=[COORD if d>0 else DELIB for d in B.delta]
axB.barh(y,B.delta,color=bcol,zorder=3)
for yi,(_,r) in zip(y,B.iterrows()):
    off=0.12 if r.delta>0 else -0.12; ha="left" if r.delta>0 else "right"
    axB.text(r.delta+off,yi,f"{r.delta:+.1f}{r.sig}",va="center",ha=ha,fontsize=8)
axB.axvline(0,color="#444",lw=.8)
axB.set_yticks(y); axB.set_yticklabels(labels,fontsize=8.3)
axB.set_xlabel("Δ rate per 100 utterances  (REVIEW − IDS)",fontsize=9.5)
xlim=max(abs(B.delta))*1.35; axB.set_xlim(-xlim,xlim)
axB.set_title("B  Content that distinguishes the stages\n(per-meeting paired Wilcoxon, BH-FDR; "
              "***q<.001 *q<.05)",fontsize=10.5,loc="left")
axB.text(.97,.04,"← deliberation content (IDS)",transform=axB.transAxes,ha="right",
         color=DELIB,fontsize=8.5,fontstyle="italic")
axB.text(.03,.96,"procedural / info (review) →",transform=axB.transAxes,ha="left",va="top",
         color=COORD,fontsize=8.5,fontstyle="italic")

fig.suptitle("EOS Level 10 agenda stages: the floor reorganizes in the procedural review, "
             "while deliberation content concentrates in IDS",fontsize=11.5,y=0.99)
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig("fig_l10_stages.png",dpi=150)
print("wrote fig_l10_stages.png")
