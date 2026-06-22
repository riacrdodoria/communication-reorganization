"""Paper figure — Study 3: the taxonomy fingerprint of reorganization (coordination, not deliberation)."""
import numpy as np,pandas as pd,os
import matplotlib.pyplot as plt
import paper_style as ps
ps.setup()
LSH=os.path.expanduser("~/lsh-work")
df=pd.read_csv(f"{LSH}/peaks_taxonomy_sig.csv")
d=df[(df.metric=="rmse_g")&(df.side=="peak")].copy()
TAX={**{c:"CACS" for c in['arguable','converge','disagree','delim','nonarg']},
 **{c:"IAM" for c in['iam1','iam2','iam3','iam4','iam5']},**{c:"Mercer" for c in['disput','cumul','explor']},
 **{c:"Bales" for c in['bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin','basksug','bsolid','btension','bagree','bdisagree','btensh','bantag']},
 **{c:"act4teams" for c in['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans','coop']},
 **{c:"ISO" for c in['qset','qprop','directive','commissive','feedback']}}
LAB={'arguable':'arguable','converge':'convergent','disagree':'disagreement','delim':'delimiting','nonarg':'non-arguable',
 'iam1':'sharing','iam2':'dissonance','iam3':'negotiation','iam4':'testing','iam5':'agreement','disput':'disputational',
 'cumul':'cumulative','explor':'exploratory','bgiveinfo':'gives information','bgiveopin':'gives opinion',
 'bgivesug':'gives suggestion','baskinfo':'asks information','baskopin':'asks opinion','basksug':'asks suggestion',
 'bsolid':'solidarity','btension':'tension release','bagree':'agrees','bdisagree':'disagrees','btensh':'shows tension',
 'bantag':'antagonism','namep':'names problem','linkp':'links problem','names':'names solution','links':'links solution',
 'linkc':'links to consequence','cprod':'procedural','proact':'proactive','struct':'structuring','ginfo':'gives information',
 'ktrans':'knowledge transfer','coop':'cooperation','qset':'set-question','qprop':'propositional question',
 'directive':'directive','commissive':'commissive','feedback':'feedback'}
d=d[d.cat.isin(TAX)].copy()
d["tax"]=d.cat.map(TAX); d["label"]=d.cat.map(LAB)
d=d.sort_values("mean_lift")
sig=(d.q_fdr<.05).sum()
y=np.arange(len(d))
col=[ps.COORD if v>0 else ps.DELIB for v in d.mean_lift]
fig,ax=plt.subplots(figsize=(8.4,9.2))
ax.hlines(y,0,d.mean_lift,color=col,lw=2.4,zorder=2)
ax.scatter(d.mean_lift,y,color=col,s=46,zorder=3,edgecolor="white",lw=.8)
for yi,(_,r) in zip(y,d.iterrows()):
    star="***" if r.q_fdr<.001 else "**" if r.q_fdr<.01 else "*" if r.q_fdr<.05 else ""
    off=.012 if r.mean_lift>=0 else -.012; ha="left" if r.mean_lift>=0 else "right"
    ax.text(r.mean_lift+off,yi,f"{r.tax}: {r.label} {star}",va="center",ha=ha,fontsize=7.4,color=ps.INK)
ax.axvline(0,color=ps.INK,lw=.9)
ax.set_yticks([]); ax.set_xlim(-.95,1.45)
ax.set_xlabel("content lift at reorganization events  (Δ code density, peaks − baseline)")
ax.set_title("Study 3 — Reorganization is coordination, not deliberation",loc="left")
# pole headers in the empty quadrants (top-left, bottom-right) to avoid the lollipop labels
ax.text(-.62,len(d)-2.2,"COORDINATION\nenriched at\nreorganization",color=ps.COORD,fontsize=9.5,
        ha="center",va="top",fontweight="bold",linespacing=1.3)
ax.text(.95,3.2,"DELIBERATION\nsuppressed at\nreorganization",color=ps.DELIB,fontsize=9.5,
        ha="center",va="bottom",fontweight="bold",linespacing=1.3)
ps.statbox(ax,"Test  per-meeting code-density lift at RMSE\nreorganization events (>mean+2.33 SD) vs\n"
              "baseline; Wilcoxon signed-rank across\nmeetings, Benjamini–Hochberg FDR.\n"
              f"Unit  meeting (n = 34).   Sig  {sig}/40 categories (q<.05).\n"
              "6 validated taxonomies · 40 categories.",loc="lower right")
ps.caption(fig,"Figure 3. Across all six validated coding schemes, the categories enriched when team "
   "communication reorganizes are coordinative/procedural (information-seeking, feedback, agreement, "
   "structuring; teal), while argumentation and solution-construction categories are suppressed (orange). "
   "Bars = mean within-meeting density lift at reorganization events vs baseline; *q<.05, **q<.01, ***q<.001 (BH-FDR).",y=-0.02)
fig.tight_layout(rect=[0,0.02,1,1])
ps.save(fig,"fig_paper_S3_taxonomy_fingerprint")
