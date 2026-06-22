"""Paper figure — Study 6: dialogue microstructure.
A) Topic-episode boundaries ARE reorganization events (naturalistic perturbation): entropy↑, %DET↓ in
   ±30s of a boundary vs episode interior; paired Wilcoxon across meetings.
B) The EOS Level 10 agenda externalises it: the procedural REVIEW reorganizes more than problem-solving IDS."""
import numpy as np,pandas as pd,os,glob
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon
import paper_style as ps
ps.setup()
L=os.path.expanduser("~/lsh-work"); GM=f"{L}/data/metrics_gorman_l8"
EP=pd.read_csv(f"{L}/episode_codes.csv")
# --- A: recompute boundary perturbation (topic-episode starts) ---
rows=[]
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    g=pd.read_csv(f); sec=g.second.to_numpy(float); ent=g.entropy_g.to_numpy(float); det=g.det_g.to_numpy(float)
    bnds=[b for b in sorted(EP[EP.mid==mid].sec_start.tolist()) if b>sec.min()+30]
    if not bnds: continue
    near=np.zeros(len(sec),bool)
    for b in bnds: near|=(np.abs(sec-b)<=30)
    if near.sum()<5 or (~near).sum()<5: continue
    rows.append(dict(e_b=np.nanmean(ent[near]),e_i=np.nanmean(ent[~near]),
                     d_b=np.nanmean(det[near]),d_i=np.nanmean(det[~near])))
B=pd.DataFrame(rows)
pe=wilcoxon(B.e_b,B.e_i).pvalue; pd_=wilcoxon(B.d_b,B.d_i).pvalue
de=B.e_b.mean()-B.e_i.mean(); dd=B.d_b.mean()-B.d_i.mean()
# --- B: L10 review vs IDS ---
P=pd.read_csv(f"{L}/l10_stage_metrics.csv")
REV=["scorecard","rock_review","todo"]
rec=[]
for mid,g in P.groupby("mid"):
    rv=g[g.stage.isin(REV)]; iv=g[g.stage=="ids"]
    if len(rv) and len(iv):
        rec.append((np.average(rv.entropy,weights=rv.secs),iv.entropy.mean(),
                    np.average(rv.reorg_rate,weights=rv.secs),iv.reorg_rate.mean()))
R=pd.DataFrame(rec,columns=["rev_e","ids_e","rev_r","ids_r"])
pe2=wilcoxon(R.rev_e,R.ids_e).pvalue; pr2=wilcoxon(R.rev_r,R.ids_r).pvalue

fig,(axA,axB)=plt.subplots(1,2,figsize=(13,5.6),gridspec_kw={"width_ratios":[1,1.05]})
# Panel A grouped bars boundary vs interior (entropy & %DET)
x=np.arange(2); w=.36
axA.bar(x-w/2,[B.e_b.mean(),B.d_b.mean()],w,color=ps.DELIB,label="±30 s of boundary",zorder=3)
axA.bar(x+w/2,[B.e_i.mean(),B.d_i.mean()],w,color=ps.COORD,label="episode interior",zorder=3)
for xi,vb,vi in zip(x,[B.e_b.mean(),B.d_b.mean()],[B.e_i.mean(),B.d_i.mean()]):
    axA.text(xi-w/2,vb+0.6,f"{vb:.1f}",ha="center",fontsize=8.5); axA.text(xi+w/2,vi+0.6,f"{vi:.1f}",ha="center",fontsize=8.5)
axA.set_xticks(x); axA.set_xticklabels(["team-state entropy\n(↑ reorganization)","%DET\n(↓ reorganization)"])
axA.set_ylabel("metric value"); axA.set_ylim(0,95); axA.legend(loc="upper center",fontsize=8.5)
axA.set_title("A  Topic boundaries ARE reorganization events",loc="left",fontsize=11)
ps.statbox(axA,f"±30 s of a topic-episode boundary vs interior;\npaired Wilcoxon across meetings (n={len(B)}).\n"
              f"Δentropy = {de:+.1f} {ps.stars(pe)}    Δ%DET = {dd:+.1f} {ps.stars(pd_)}\n"
              "Non-circular: boundaries from content,\nmetrics from turn-taking only.",loc="lower left",fontsize=7.6)
# Panel B L10 review vs IDS
x2=np.arange(2);
axB.bar(x2-w/2,[R.rev_e.mean(),R.rev_r.mean()],w,color=ps.COORD,label="procedural review\n(scorecard/rock/to-do)",zorder=3)
axB.bar(x2+w/2,[R.ids_e.mean(),R.ids_r.mean()],w,color=ps.DELIB,label="IDS (problem-solving)",zorder=3)
for xi,a,b in zip(x2,[R.rev_e.mean(),R.rev_r.mean()],[R.ids_e.mean(),R.ids_r.mean()]):
    axB.text(xi-w/2,a+0.4,f"{a:.1f}",ha="center",fontsize=8.5); axB.text(xi+w/2,b+0.4,f"{b:.1f}",ha="center",fontsize=8.5)
axB.set_xticks(x2); axB.set_xticklabels(["team-state entropy","reorg-event rate (%)"])
axB.set_ylabel("value"); axB.set_ylim(0,45); axB.legend(loc="upper right",fontsize=8)
axB.set_title("B  The EOS Level 10 agenda externalises it",loc="left",fontsize=11)
ps.statbox(axB,f"per-meeting paired Wilcoxon (n={len(R)}).\n"
              f"entropy: review>IDS Δ=+{R.rev_e.mean()-R.ids_e.mean():.1f} {ps.stars(pe2)}\n"
              f"reorg rate: review>IDS Δ=+{R.rev_r.mean()-R.ids_r.mean():.1f} {ps.stars(pr2)}\n"
              "the procedural review reorganizes MORE\nthan problem-solving (= coordination).",loc="lower left",fontsize=7.6)
fig.suptitle("Study 6 — Reorganization is a topic-transition phenomenon, legible in the meeting's real agenda",
             fontsize=12.5,fontweight="bold",x=.01,ha="left")
ps.caption(fig,"Figure 6. (A) In ±30 s of a topic-episode boundary, team-state entropy rises and %DET falls "
  "vs episode interiors — topic transitions are the naturalistic perturbation that drives reorganization "
  "(non-circular: boundaries are lexical, metrics are turn-taking). (B) On the EOS Level 10 agenda these "
  "teams run, the procedural review stages reorganize more than the problem-solving (IDS) block — "
  "reorganization is coordination, not deliberation. Paired Wilcoxon; *p<.05, **p<.01, ***p<.001.",y=-0.03)
fig.tight_layout(rect=[0,0.02,1,.96])
ps.save(fig,"fig_paper_S6_microstructure")
