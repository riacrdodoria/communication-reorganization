"""Supplementary Figure S1 — Four intuitive results that do not survive an adequate null.
A: lexical topic boundaries (utterance-count TF-IDF tiling) fall in the collaborative floor and coincide with
   reorganization events about as much when utterance texts are shuffled (keeping who spoke when) as with the real text;
   semantic segmentations do not. B: rising %DET variance before events also appears before surrogate events and is
   absent for isolated events. C: event pairing (30-75 s intervals) is mostly produced by the detection rule. D: weaker
   reciprocity and facilitator advantage near events vanish once local entropy is controlled.
(The size of entropy excursions, a fifth case, is in Figure 2B.)"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import wilcoxon
import paper_style as ps
ps.setup(); R = os.path.expanduser("~/lsh-work/study13_metric_extensions/results"); INK, MUTED, BLUE = ps.INK, ps.NEUTRAL, "#1f6fb4"
fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4)); (axA, axB), (axC, axD) = axs; fig.subplots_adjust(hspace=.7, wspace=.45)
# A
FS = pd.read_csv(f"{R}/topic_tri_floorstate.csv").set_index("seg"); RL = pd.read_csv(f"{R}/topic_tri_relations.csv").set_index("seg")
segs = [("TILE", "lexical tiling\n(original)"), ("EMB", "sentence\nembeddings"), ("NETC", "semantic\nnetwork"), ("NETG", "network\nchange")]
for i, (k, lab) in enumerate(segs):
    axA.bar(i - .2, FS.loc[k, "F2"], .36, color=BLUE, label="real text" if i == 0 else None); axA.bar(i + .2, FS.loc[k, "F2_shuf"], .36, color="#c9d1da", label="shuffled text" if i == 0 else None)
    axA.errorbar(i + .2, FS.loc[k, "F2_shuf"], yerr=[[FS.loc[k, "F2_shuf"] - FS.loc[k, "F2_shuf_lo"]], [FS.loc[k, "F2_shuf_hi"] - FS.loc[k, "F2_shuf"]]], fmt="none", ecolor=INK, capsize=2, lw=.8)
axA.axhline(1, color=MUTED, ls=":", lw=.7); axA.set_xticks(range(4)); axA.set_xticklabels([l for _, l in segs], fontsize=5.8); axA.tick_params(axis="y", labelsize=5.8)
axA.set_ylabel("topic boundaries in collaborative\nfloor / expected", fontsize=6.2); axA.legend(fontsize=5.4, frameon=False, loc="upper right")
axA.set_title("A. Lexical topics follow turn rhythm", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# B
CT = pd.read_csv(f"{R}/csd_tautology.csv"); CT["all_d"] = CT.all_ev - CT.all_base; CT["iso_d"] = CT.iso_ev - CT.iso_base
bars = [("real events", CT.all_d), ("surrogate\nevents", CT.sur_all), ("real, isolated\nevents", CT.iso_d), ("surrogate,\nisolated", CT.sur_iso)]
for i, (lab, v) in enumerate(bars):
    v = v.dropna(); axB.bar(i, v.mean(), .6, color=BLUE if i % 2 == 0 else "#c9d1da"); axB.errorbar(i, v.mean(), yerr=v.sem(), fmt="none", ecolor=INK, capsize=2, lw=.8)
axB.axhline(0, color=MUTED, lw=.7); axB.set_xticks(range(4)); axB.set_xticklabels([b[0] for b in bars], fontsize=5.8); axB.tick_params(axis="y", labelsize=5.8)
axB.set_ylabel("rise of %DET variance before onset\n(Kendall tau, event − baseline)", fontsize=6.2)
axB.set_title("B. 'Early warning' is built in", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# C
CL = pd.read_csv(f"{R}/cluster_tautology.csv")
for _, r in CL.iterrows(): axC.plot([0, 1], [r.pair_sur, r.pair], color="#9fb6d6", lw=.6)
axC.scatter(np.zeros(len(CL)), CL.pair_sur, s=8, color="#8a939e"); axC.scatter(np.ones(len(CL)), CL.pair, s=8, color=BLUE)
axC.plot([0, 1], [CL.pair_sur.mean(), CL.pair.mean()], color=INK, lw=2); p = wilcoxon(CL.pair - CL.pair_sur).pvalue
axC.text(.5, .97, f"{CL.pair_sur.mean():.3f} → {CL.pair.mean():.3f} (p = {p:.3f})", transform=axC.transAxes, ha="center", va="top", fontsize=5.8, color=INK)
axC.set_xticks([0, 1]); axC.set_xticklabels(["surrogate events", "real events"], fontsize=6); axC.set_xlim(-.3, 1.3); axC.tick_params(axis="y", labelsize=5.8)
axC.set_ylabel("share of inter-event intervals 30-75 s", fontsize=6.2); axC.set_title("C. Event pairs come mostly\nfrom detection", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# D
RA = pd.read_csv(f"{R}/rem_artifacts.csv")
def orp(model, term):
    r = RA[(RA.model == model) & (RA.term == term)].iloc[0]; return np.exp(r.coef), np.exp(r.coef - 1.96 * r.se), np.exp(r.coef + 1.96 * r.se)
items = [("reciprocity × near event", "recip_x_near"), ("facilitator × near event", "fac_x_near")]
for i, (lab, term) in enumerate(items):
    for j, (model, ml, c) in enumerate([("near only", "without control", BLUE), ("near + local-entropy controls", "controlling local entropy", "#8a939e")]):
        o, lo, hi = orp(model, term); y = i + (j - .5) * .3
        axD.plot([lo, hi], [y, y], color=c, lw=1.4); axD.scatter(o, y, s=22, color=c, zorder=3, label=ml if i == 0 else None)
axD.axvline(1, color=MUTED, ls=":", lw=.7); axD.set_yticks(range(len(items))); axD.set_yticklabels([l for l, _ in items], fontsize=6); axD.grid(axis="y", visible=False)
axD.set_xlabel("odds ratio of taking the next turn (95 % CI)", fontsize=6.2); axD.tick_params(axis="x", labelsize=5.8); axD.legend(fontsize=5.4, frameon=False, loc="upper center", bbox_to_anchor=(.4, -.2), ncol=2); axD.set_ylim(1.5, -.5)
axD.set_title("D. 'The floor opens at events'\nis local entropy", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/figS1_method_traps.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok")
