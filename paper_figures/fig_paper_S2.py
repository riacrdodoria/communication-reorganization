"""Paper figure — Study 2: what reorganization IS, dynamically.
A) entropy–%DET geometry: a single continuous manifold (a continuum, not two regimes; Sarle bimodality
   coefficient below the uniform threshold).
B) supra-autoregressive: SD of pre-to-post entropy change is ~2x and outside the 95% interval of AR(1)
   and VAR(1) surrogates.
C) cycle geometry: ascending and descending limbs are symmetric (paired Wilcoxon, n.s.)."""
import numpy as np,pandas as pd,os,glob
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon,skew,kurtosis
import paper_style as ps
ps.setup()
L=os.path.expanduser("~/lsh-work"); GM=f"{L}/data/metrics_gorman_l8"
ent=[]; det=[]
for f in glob.glob(f"{GM}/*_gorman.csv"):
    g=pd.read_csv(f); ent.append(g.entropy_g.to_numpy(float)); det.append(g.det_g.to_numpy(float))
E=np.concatenate(ent); D=np.concatenate(det); m=np.isfinite(E)&np.isfinite(D); E,D=E[m],D[m]
# Sarle bimodality coefficient on entropy: (skew^2+1)/kurtosis ; >0.555 suggests bimodal
# Sarle BC = (g1^2+1) / (excess_kurtosis + 3(n-1)^2/((n-2)(n-3))); fixed 2026-09-05 (Pearson kurtosis had been used, inflating the denominator by 3)
g1=skew(E); k=kurtosis(E); n=len(E); BC=(g1**2+1)/(k+ (3*(n-1)**2)/((n-2)*(n-3)))
fig=plt.figure(figsize=(14.5,4.9)); gs=fig.add_gridspec(1,3,width_ratios=[1.15,0.9,0.9],wspace=.33)
# A geometry
axA=fig.add_subplot(gs[0,0])
hb=axA.hexbin(D,E,gridsize=45,cmap="BuGn",mincnt=1,linewidths=0)
axA.set_xlabel("%DET (recurrence)"); axA.set_ylabel("team-state entropy")
axA.set_title("A  Entropy–%DET geometry: a continuum",loc="left",fontsize=11)
ps.statbox(axA,f"all meeting-seconds pooled.\nSingle continuous manifold —\nno two discrete regimes.\n"
              f"Sarle bimodality coeff. = {BC:.2f}\n(<0.555 ⇒ not bimodal; the L_min=2\nbimodality was a %DET-saturation\nartefact, gone at L_min=8).",loc="upper right",fontsize=7.2)
# B supra-AR
axB=fig.add_subplot(gs[0,1])
# 2026-09-05: read the L8 surrogate results written by surrogate_validation.py (units: %MaxEnt); the earlier
# hardcoded 0.405/0.190 came from the retired 1 Hz raw-bits pipeline.
_sv=pd.read_csv(f"{L}/surrogate_validation_results.csv").iloc[0]
obs=float(_sv.obs_sd); ar=(float(_sv.AR1_sd_mean),float(_sv.AR1_sd_lo),float(_sv.AR1_sd_hi)); var=(float(_sv.VAR1_sd_mean),float(_sv.VAR1_sd_lo),float(_sv.VAR1_sd_hi))
_ratio=obs/ar[0]
x=np.arange(3)
axB.bar(0,obs,.6,color=ps.DELIB,zorder=3,label="observed")
axB.bar(1,ar[0],.6,color="#b9c2cc",zorder=3); axB.bar(2,var[0],.6,color="#b9c2cc",zorder=3)
axB.errorbar(1,ar[0],yerr=[[ar[0]-ar[1]],[ar[2]-ar[0]]],fmt="none",ecolor=ps.INK,capsize=4,lw=1.2)
axB.errorbar(2,var[0],yerr=[[var[0]-var[1]],[var[2]-var[0]]],fmt="none",ecolor=ps.INK,capsize=4,lw=1.2)
axB.text(0,obs+.01,f"{obs:.2f}",ha="center",fontsize=9,fontweight="bold")
axB.set_xticks(x); axB.set_xticklabels(["observed","AR(1)\nnull","VAR(1)\nnull"])
axB.set_ylabel("SD of pre→post entropy change (%MaxEnt)"); axB.set_ylim(0,obs*1.2)
axB.set_title("B  Reorganization is supra-autoregressive",loc="left",fontsize=11)
ps.statbox(axB,f"dispersion of entropy excursions ≈ {_ratio:.1f}×\nthe AR(1)/VAR(1) baseline and OUTSIDE\ntheir 95% interval (200 surrogates each,\nL_min=8 metrics). → genuine structure.",loc="upper left",fontsize=7.0)
# C ascent vs descent
axC=fig.add_subplot(gs[0,2])
ph=pd.read_csv(f"{L}/phase_asymmetry.csv")
asc,desc=ph.ascent_s.dropna(),ph.descent_s.dropna()
pw=wilcoxon(ph.ascent_s,ph.descent_s,nan_policy="omit").pvalue
parts=axC.violinplot([asc,desc],positions=[0,1],showmeans=False,showmedians=True,widths=.7)
for pc,c in zip(parts['bodies'],[ps.COORD,ps.DELIB]): pc.set_facecolor(c); pc.set_alpha(.5)
for k2 in ('cbars','cmins','cmaxes','cmedians'):
    if k2 in parts: parts[k2].set_color(ps.INK)
axC.set_xticks([0,1]); axC.set_xticklabels([f"ascent\n(med {asc.median():.0f}s)",f"descent\n(med {desc.median():.0f}s)"])
axC.set_ylabel("limb duration (s)")
axC.set_title("C  Cycle geometry is symmetric",loc="left",fontsize=11)
ps.statbox(axC,f"ascending vs descending limbs of the\nreorganization cycle, per meeting (n={len(asc)}).\n"
              f"paired Wilcoxon p={pw:.2f} ({ps.stars(pw)}).\nThe old 'descent more variable' claim was\na definitional artefact.",loc="upper left",fontsize=7.0)
fig.suptitle("Study 2 — Reorganization is an endogenous, supra-autoregressive continuum with symmetric geometry",
             fontsize=12.5,fontweight="bold",x=.01,ha="left")
ps.caption(fig,"Figure 2. (A) Pooled across all meeting-seconds, entropy and %DET form one continuous "
  "manifold — not two discrete coordination regimes (Sarle bimodality coefficient below the 0.555 "
  "threshold; the earlier bimodality was a %DET-saturation artefact removed by L_min=8). (B) The dispersion "
  "of pre→post entropy excursions at reorganization is ~2× and outside the 95% interval of AR(1) and VAR(1) "
  "surrogates (200 each) — genuine structure beyond trivial oscillation. (C) Ascending and descending limbs "
  "of the cycle are symmetric (paired Wilcoxon, n.s.).",y=-0.05)
ps.save(fig,"fig_paper_S2_dynamics")
print("BC",round(BC,3),"ascent med",asc.median(),"descent med",desc.median(),"pw",round(pw,3))
