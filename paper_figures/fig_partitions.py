"""Figure — Six ways of dividing a meeting in time, and how they relate (Study 13, partitions.py).
A: one meeting, the six boundary sets on a common timeline (agenda stages shaded).
B: co-occurrence matrix, observed / expected share of reference boundaries with a target boundary within +/-30 s
   (expected from 1000 circular shifts); log2 diverging scale, gray = chance.
C: time scale of each partition (median segment length; boundaries per hour)."""
import os, json, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import paper_style as ps
ps.setup()
R = os.path.expanduser("~/lsh-work/study13_metric_extensions/results")
P = pd.read_csv(f"{R}/partitions_pairs.csv"); S = pd.read_csv(f"{R}/partitions_scale.csv").set_index("partition"); B = json.load(open(f"{R}/partitions_bounds.json"))
NAMES = ["agenda", "topic", "event", "level", "floor", "novelty"]
LAB = {"agenda": "Pulso script stage", "topic": "semantic topic", "event": "reorganization event", "level": "entropy level shift",
       "floor": "extended floor turn (≥30 s)", "novelty": "lexical novelty peak"}
STAGE_LAB = {"segue": "check-in", "scorecard": "scorecard", "rock_review": "rocks", "headlines": "headlines", "todo": "to-dos", "ids": "IDS", "conclude": "close"}
INK, MUTED = ps.INK, ps.NEUTRAL
fig = plt.figure(figsize=(7.2, 6.6))
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], width_ratios=[1.35, 1.0], hspace=.55, wspace=.55)
axA = fig.add_subplot(gs[0, :]); axB = fig.add_subplot(gs[1, 0]); axC = fig.add_subplot(gs[1, 1])

# --- A: one meeting ------------------------------------------------------------------------------------------
import sys; sys.path.insert(0, os.path.expanduser("~/lsh-work/study13_metric_extensions/src")); import common as C
cand = [m for m in B if len(C.stage_segments(m)) == 7]; mid = sorted(cand, key=lambda m: abs(B[m]["T"] - 5400))[0]
segs = C.stage_segments(mid); T = B[mid]["T"] / 60
for k, (n, a, b) in enumerate(segs):
    axA.axvspan(a / 60, b / 60, color="#eceae6" if k % 2 == 0 else "#f7f6f3", zorder=0, lw=0)
    axA.text((a + b) / 120, 6.25 + .45 * (k % 2), STAGE_LAB.get(n, n), ha="center", va="bottom", fontsize=5.6, color=MUTED)
for i, nm in enumerate(NAMES):
    y = 5 - i; x = np.array(B[mid][nm]) / 60
    axA.vlines(x, y - .32, y + .32, color=INK, lw=.9 if nm != "agenda" else 1.6)
    axA.text(-1.2, y, LAB[nm], ha="right", va="center", fontsize=6.4, color=INK)
axA.axhline(2.5, color=MUTED, lw=.5, ls=":")
for y0, y1, t in [(3.0, 5.4, "collective\ntransitions"), (-.4, 2.0, "individual\nfloor flow")]:
    axA.plot([T + 1.2] * 2, [y0, y1], color=MUTED, lw=.8, clip_on=False); axA.text(T + 1.8, (y0 + y1) / 2, t, fontsize=6, color=MUTED, va="center", ha="left")
axA.set_xlim(0, T); axA.set_ylim(-.7, 7.2); axA.grid(False); axA.set_yticks([]); axA.set_xlabel("meeting time (min)", fontsize=7.2)
for s_ in ("left", "right", "top"): axA.spines[s_].set_visible(False)
axA.set_title("A. One meeting, six divisions of its time", loc="left", fontsize=8.8, fontweight="bold", color=ps.COORD, x=-0.24)

# --- B: co-occurrence matrix ---------------------------------------------------------------------------------
Q = P[P.W == 30]; M = Q.pivot(index="ref", columns="target", values="ratio").loc[NAMES, NAMES]
pe = Q.pivot(index="ref", columns="target", values="p_enrich").loc[NAMES, NAMES]; pdp = Q.pivot(index="ref", columns="target", values="p_deplete").loc[NAMES, NAMES]
cmap = LinearSegmentedColormap.from_list("div", ["#2166ac", "#92c5de", "#f0efec", "#f4a582", "#b2182b"])
axB.grid(False); Lg = np.log2(M.to_numpy(float)); im = axB.imshow(np.ma.masked_invalid(Lg), cmap=cmap, norm=TwoSlopeNorm(0, -1, 1))
for i in range(6):
    for j in range(6):
        if i == j: axB.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, color="white")); continue
        r = M.iloc[i, j]; star = "*" if pe.iloc[i, j] < .01 else ("°" if pdp.iloc[i, j] < .01 else "")
        axB.text(j, i, f"{r:.2f}{star}", ha="center", va="center", fontsize=5.6, color=INK)
short = ["script", "topic", "event", "level", "floor", "novelty"]
axB.set_xticks(range(6)); axB.set_xticklabels(short, fontsize=6.4, rotation=35, ha="right"); axB.set_yticks(range(6)); axB.set_yticklabels(short, fontsize=6.4)
for v in (2.5,): axB.axhline(v, color=INK, lw=.8); axB.axvline(v, color=INK, lw=.8)
axB.set_xlabel("target boundary", fontsize=6.8); axB.set_ylabel("reference boundary", fontsize=6.8)
cb = fig.colorbar(im, ax=axB, fraction=.046, pad=.03, ticks=[-1, -.5, 0, .5, 1]); cb.ax.set_yticklabels(["0.5×", "0.7×", "chance", "1.4×", "2×"], fontsize=5.6)
axB.set_title("B. Which divisions coincide (±30 s)", loc="left", fontsize=8.8, fontweight="bold", color=ps.COORD)
axB.text(0.0, -0.36, "* above chance, ° below chance (p < .01, 1,000 circular shifts)", fontsize=5.4, color=MUTED, transform=axB.transAxes)

# --- C: time scale --------------------------------------------------------------------------------------------
y = np.arange(6)[::-1]
axC.hlines(y, 30, S.loc[NAMES, "median_segment_s"], color="#b9c2cc", lw=2.2)
axC.scatter(S.loc[NAMES, "median_segment_s"], y, s=26, color=INK, zorder=3)
for yy, nm in zip(y, NAMES):
    axC.text(S.loc[nm, "median_segment_s"] * 1.25, yy, f"{S.loc[nm,'median_segment_s']/60:.1f} min · {S.loc[nm,'per_hour']:.0f}/h", va="center", fontsize=5.8, color=INK)
axC.set_xscale("log"); axC.minorticks_off(); axC.grid(axis="y", visible=False); axC.set_xlim(30, 3000); axC.set_xticks([60, 120, 300, 600]); axC.set_xticklabels(["1", "2", "5", "10"], fontsize=6.4)
axC.set_yticks(y); axC.set_yticklabels(short, fontsize=6.4); axC.axhline(2.5, color=MUTED, lw=.5, ls=":")
axC.set_xlabel("median segment length (min, log scale)", fontsize=6.8)
axC.set_title("C. Time scale of each division", loc="left", fontsize=8.8, fontweight="bold", color=ps.COORD)

for ext in ("png", "pdf"):
    fig.savefig(f"{os.path.dirname(__file__)}/fig_partitions.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("wrote fig_partitions; example meeting", mid)
