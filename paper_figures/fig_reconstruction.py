"""Figure — Reconstructing the team-state series from onset-only transcripts (Paper 1, Study 1).
Same logic as the earlier Last-Speaker-Holds representation, within-session and between-session figures, now with the
word-timed reconstruction (LSH-WD) that every metric in the paper uses, and pure Last-Speaker-Holds (LSH) for contrast.
Data: 15 archival sessions of Gorman et al. (2020) with hand-coded onsets and offsets
(~/lsh-work/study1_lsh_validation/results/lsh_variants_team.csv, lsh_variants_excerpt.npz).
Panels: A representation of one minute (true standard, pure LSH, LSH-WD); B within-session r by metric; C event agreement
and silence share by reconstruction; D-F between-session means, true standard vs reconstruction."""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import pearsonr
import paper_style as ps
ps.setup()
R = os.path.expanduser("~/lsh-work/study1_lsh_validation/results")
T = pd.read_csv(f"{R}/lsh_variants_team.csv"); Z = np.load(f"{R}/lsh_variants_excerpt.npz")
DOM = {"submarine": "#4C72B0", "surgical": "#C44E52"}
VAR = {"LSH": ("pure LSH", ps.NEUTRAL), "LSH-WD": ("LSH-WD", ps.COORD)}

fig = plt.figure(figsize=(7.2, 7.4))
gs = fig.add_gridspec(3, 6, height_ratios=[0.8, 1.0, 1.0], hspace=.75, wspace=1.2)
axA = fig.add_subplot(gs[0, :]); axB = fig.add_subplot(gs[1, :4]); axC = fig.add_subplot(gs[1, 4]); axC2 = fig.add_subplot(gs[1, 5])
axD = [fig.add_subplot(gs[2, 2 * k:2 * k + 2]) for k in range(3)]

# --- A: one minute, three rows -------------------------------------------------------------------------------
std = Z["standard"]; L0 = 60
best, b0 = -1, 0
for a in range(0, std.size - L0, 5):  # a minute with several speakers and real silence
    w = std[a:a + L0]; sil = (w == 0).mean(); sw = (np.diff(w) != 0).sum()
    if .2 <= sil <= .4 and len(set(w[w > 0])) >= 3 and sw > best: best, b0 = sw, a
rows = [("true standard\n(hand-coded offsets)", std), ("pure LSH\n(holds to next onset)", Z["LSH"]), ("LSH-WD\n(0.5 s per word, then silence)", Z["LSH-WD"])]
spk = sorted(set(np.concatenate([r[1][b0:b0 + L0] for r in rows])) - {0}); cmap = plt.get_cmap("tab10"); col = {s: cmap(i % 10) for i, s in enumerate(spk)}
for k, (lab, s) in enumerate(rows):
    y = 2 - k; w = s[b0:b0 + L0]
    for t, v in enumerate(w):
        axA.add_patch(plt.Rectangle((t, y - .38), 1, .76, facecolor="white" if v == 0 else col[v], edgecolor="#cbd5e1" if v == 0 else "none", lw=.4))
    axA.text(-1.2, y, lab, ha="right", va="center", fontsize=6.4, color=ps.INK)
axA.set_xlim(-22, 61); axA.set_ylim(-.6, 2.6); axA.set_yticks([]); axA.set_xticks([0, 15, 30, 45, 60])
for sp_ in ("left", "right", "top"): axA.spines[sp_].set_visible(False)
axA.set_xlabel("seconds (one-minute excerpt of a surgical-team session)", fontsize=6.8)
axA.set_title("A. Three representations of the same minute of talk", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axA.text(60, 2.5, "colour = speaker; white = no one speaking", ha="right", fontsize=5.8, color=ps.INK)

# --- B: within-session r, by metric and reconstruction (HF Figure 5 logic) -----------------------------------
mets = [("r_entropy", "Entropy"), ("r_det", "%DET"), ("r_rmse", "RMSE")]
rng = np.random.default_rng(0)
for i, (c, lab) in enumerate(mets):
    for j, v in enumerate(["LSH", "LSH-WD"]):
        x0 = i * 3 + j; d = T[T.variant == v]
        axB.boxplot(d[c], positions=[x0], widths=.6, showfliers=False, patch_artist=True,
                    boxprops=dict(facecolor=VAR[v][1], alpha=.25, color=VAR[v][1]), medianprops=dict(color=VAR[v][1], lw=1.4),
                    whiskerprops=dict(color=VAR[v][1]), capprops=dict(color=VAR[v][1]))
        axB.scatter(x0 + rng.uniform(-.17, .17, len(d)), d[c], s=10, c=[DOM[x] for x in d.domain], edgecolor="white", lw=.3, zorder=3)
        axB.text(x0, 1.03, f"{d[c].mean():.2f}", ha="center", fontsize=6, color=VAR[v][1], fontweight="bold")
axB.axhline(.8, color=ps.NEUTRAL, ls=":", lw=.8)
axB.set_xticks([0.5, 3.5, 6.5]); axB.set_xticklabels([m[1] for m in mets], fontsize=7.4); axB.set_ylim(0.2, 1.08)
axB.set_ylabel("within-session r with\nthe true standard series", fontsize=7.2)
axB.set_title("B. Moment-to-moment agreement", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
axB.legend(handles=[Patch(facecolor=VAR["LSH"][1], alpha=.35, label="pure LSH"), Patch(facecolor=VAR["LSH-WD"][1], alpha=.35, label="LSH-WD"),
                    Line2D([], [], marker="o", ls="", color=DOM["submarine"], label="submarine", ms=4), Line2D([], [], marker="o", ls="", color=DOM["surgical"], label="surgical", ms=4)],
           fontsize=5.6, loc="lower left", ncol=2, frameon=False)

# --- C: event agreement and silence share by reconstruction (two small panels, one scale each) ---------------
order = ["LSH", "LSH-CAP3", "LSH-CAP10", "LSH-WD"]; labs = ["pure LSH", "cap 3 s", "cap 10 s", "LSH-WD"]
S = T.groupby("variant")[["events_std_matched", "silence_variant", "silence_true"]].mean().loc[order]
yc = np.arange(4)[::-1]; colsC = [ps.NEUTRAL, "#b9c2cc", "#b9c2cc", ps.COORD]
axC.barh(yc, 100 * S.events_std_matched, .62, color=colsC, zorder=3)
for y_, v in zip(yc, S.events_std_matched): axC.text(100 * v + 3, y_, f"{100*v:.0f}", va="center", fontsize=5.8, color=ps.INK)
axC.set_yticks(yc); axC.set_yticklabels(labs, fontsize=6.0); axC.set_xlim(0, 100); axC.set_xticks([0, 50, 100]); axC.tick_params(axis="x", labelsize=5.8)
axC.set_xlabel("true events\nmatched (%)", fontsize=6.2); axC.grid(axis="y", visible=False)
axC2.barh(yc, S.silence_variant, .62, color=colsC, zorder=3); axC2.axvline(S.silence_true.iloc[0], color=ps.INK, ls="--", lw=.8)
for y_, v in zip(yc, S.silence_variant): axC2.text(v + 2, y_, f"{v:.0f}", va="center", fontsize=5.8, color=ps.INK)
axC2.text(S.silence_true.iloc[0] + 1, 3.55, "true", fontsize=5.4, color=ps.INK)
axC2.set_yticks(yc); axC2.set_yticklabels([]); axC2.set_xlim(0, 70); axC2.set_xticks([0, 30, 60]); axC2.tick_params(axis="x", labelsize=5.8)
axC2.set_xlabel("silence\nshare (%)", fontsize=6.2); axC2.grid(axis="y", visible=False)
axC.set_title("C. Event timing and silence", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)

# --- D-F: between-session means (HF Figure 6 logic) ----------------------------------------------------------
for ax, (m, lab) in zip(axD, [("entropy", "Entropy (%MaxEnt)"), ("det", "%DET"), ("rmse", "RMSE")]):
    lo = []; txt = []
    for v, mk, fc in [("LSH", "o", "none"), ("LSH-WD", "o", None)]:
        d = T[T.variant == v]; x, y = d[f"mean_{m}_std"], d[f"mean_{m}_var"]; lo += [x.min(), y.min(), x.max(), y.max()]
        for dom in DOM:
            e = d[d.domain == dom]
            ax.scatter(e[f"mean_{m}_std"], e[f"mean_{m}_var"], s=14, marker=mk, facecolors=DOM[dom] if fc is None else "none",
                       edgecolors=DOM[dom] if fc is None else ps.NEUTRAL, lw=.6, zorder=3 if fc is None else 2)
        txt.append(f"{VAR[v][0]} r = {pearsonr(x, y)[0]:.2f}")
    a, b = min(lo), max(lo); pad = .05 * (b - a); ax.plot([a - pad, b + pad], [a - pad, b + pad], ls="--", color=ps.NEUTRAL, lw=.7)
    ax.set_xlim(a - pad, b + pad); ax.set_ylim(a - pad, b + pad); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"true standard", fontsize=6.6); ax.set_ylabel("reconstruction", fontsize=6.6); ax.tick_params(labelsize=5.8)
    ax.set_title(lab, fontsize=7.6, color=ps.INK)
    ax.text(.03, .97, "\n".join(txt), transform=ax.transAxes, va="top", fontsize=5.4, color=ps.INK)
axD[0].text(-.35, 1.22, "D. Session means (filled = LSH-WD, open = pure LSH)", transform=axD[0].transAxes, fontsize=8.6, fontweight="bold", color=ps.COORD)

for ext in ("png", "pdf"):
    fig.savefig(f"{os.path.dirname(__file__)}/fig_reconstruction.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("wrote fig_reconstruction; excerpt start", b0)
for m in ["entropy", "det", "rmse"]:
    for v in ["LSH", "LSH-WD"]:
        d = T[T.variant == v]; print(m, v, f"between-session r = {pearsonr(d[f'mean_{m}_std'], d[f'mean_{m}_var'])[0]:.3f}")
