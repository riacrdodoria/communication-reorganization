"""Paper figure — Study 12: the socioemotional signature of reorganization.
Panel A: event-locked lift (peak vs baseline) for the 8-category confirmatory socioemotional family,
with bootstrap 95% CIs, colored by valence. Panel B: timing within the event window (pre-onset /
onset / post-onset, 90 s grain) for the positive- and negative-composite scores."""
import numpy as np, pandas as pd, os
import matplotlib.pyplot as plt
import paper_style as ps
ps.setup()

LSH = os.path.expanduser("~/lsh-work")
S12 = f"{LSH}/study12_socioemotional/data"
POS_COL = ps.COORD          # positive valence
NEG_COL = "#b2182b"         # negative valence (distinct from DELIB orange, which denotes the
                             # deliberation pole elsewhere in this program - not reused here to avoid
                             # conflating "negative valence" with "deliberation")

lifts = pd.read_csv(f"{S12}/socioemotional_lifts.csv").sort_values("mean_lift")
timing = pd.read_csv(f"{S12}/socioemotional_timing.csv")

LAB = {"bsolid": "shows solidarity (Bales)", "btension": "tension release/jokes (Bales)",
       "bagree": "agrees (Bales)", "bdisagree": "disagrees (Bales)", "btensh": "shows tension (Bales)",
       "bantag": "shows antagonism (Bales)†", "pos": "positive socio-emotional (act4teams)",
       "neg": "negative socio-emotional (act4teams)"}

fig, axes = plt.subplots(1, 2, figsize=(13.6, 6.6), gridspec_kw={"width_ratios": [1.15, 1]})

# ---------------- Panel A: category lifts with CI ----------------
ax = axes[0]
y = np.arange(len(lifts))
col = [POS_COL if v == "+" else NEG_COL for v in lifts.valence]
xerr = np.vstack([lifts.mean_lift - lifts.ci_lo, lifts.ci_hi - lifts.mean_lift])
ax.hlines(y, 0, lifts.mean_lift, color=col, lw=2.4, zorder=2)
for yi, xi, lo, hi, c in zip(y, lifts.mean_lift, lifts.ci_lo, lifts.ci_hi, col):
    ax.errorbar([xi], [yi], xerr=[[xi - lo], [hi - xi]], fmt="none", ecolor=c, elinewidth=1.3,
                capsize=3, zorder=2)
ax.scatter(lifts.mean_lift, y, color=col, s=64, zorder=3, edgecolor="white", lw=.9)
for yi, (_, r) in zip(y, lifts.iterrows()):
    star = "***" if r.q_fdr < .001 else "**" if r.q_fdr < .01 else "*" if r.q_fdr < .05 else "n.s."
    ax.text(r.ci_hi + .012, yi, f"{LAB[r['cat']]}  {star}", va="center", ha="left", fontsize=8.4, color=ps.INK)
ax.axvline(0, color=ps.INK, lw=.9)
ax.set_yticks([]); ax.set_xlim(-.05, .62); ax.set_ylim(-1.3, len(lifts) + 1.3)
ax.set_xlabel("density lift at reorganization events\n(peak − baseline, per-meeting mean)")
ax.set_title("A.  Event-locked socioemotional lift", loc="left", pad=14)
ax.text(.975, .5, "Test  Wilcoxon + BH-FDR within 8-cat. family\n(not folded into the 40-cat. family).\n"
              "Unit  meeting (n=34). Bars = 95% bootstrap CI.\n"
              "† bantag: only 10/34 meetings (excluded).",
        transform=ax.transAxes, ha="right", va="center", fontsize=7.6, color=ps.INK, linespacing=1.35,
        bbox=dict(boxstyle="round,pad=0.45", fc="#f8fafc", ec="#cbd5e1", lw=.8), zorder=10)
ax.text(-.045, len(lifts) + 0.6, "POSITIVE", color=POS_COL, fontsize=10, fontweight="bold", va="bottom", ha="left")
ax.text(-.045, -1.0, "NEGATIVE", color=NEG_COL, fontsize=10, fontweight="bold", va="bottom", ha="left")

# ---------------- Panel B: timing (pre/at/post) ----------------
ax2 = axes[1]
xs = [0, 1, 2]
xt = ["pre-onset\nwindow", "onset\nwindow", "post-onset\nwindow"]
for label, color in [("positive composite", POS_COL), ("negative composite", NEG_COL)]:
    r = timing[timing.label == label].iloc[0]
    ys = [r.pre, r["at"], r.post]
    ax2.plot(xs, ys, "-o", color=color, lw=2.4, ms=8, zorder=3,
             label=f"{label} (n={int(r.n)} meetings)")
    star_ap = "***" if r.p_null_at_minus_pre < .001 else "**" if r.p_null_at_minus_pre < .01 else "*" if r.p_null_at_minus_pre < .05 else "n.s."
    star_pa = "***" if r.p_null_post_minus_at < .001 else "**" if r.p_null_post_minus_at < .01 else "*" if r.p_null_post_minus_at < .05 else "n.s."
    ax2.text(0.5, (ys[0] + ys[1]) / 2, star_ap, color=color, fontsize=11, ha="center",
             va="bottom" if ys[1] > ys[0] else "top", fontweight="bold")
    ax2.text(1.5, (ys[1] + ys[2]) / 2, star_pa, color=color, fontsize=11, ha="center",
             va="bottom" if ys[2] > ys[1] else "top", fontweight="bold")
ax2.set_xticks(xs); ax2.set_xticklabels(xt)
ax2.set_xlim(-.3, 2.3)
ax2.set_ylabel("mean window density (90 s grain)")
ax2.set_title("B.  Timing within the event window", loc="left")
ps.statbox(ax2, "Test  circular-shift null (2,000 seeded\nrotations) on mean(at−pre) / mean(post−at).\n"
               "Unit  meeting (n=34). Grain = 90 s windows\n(coarser than ±30 s used for second-\n"
               "resolution metrics elsewhere; disclosed).",
           loc="upper right", fontsize=7.6)
ax2.legend(loc="lower center", fontsize=8.6, frameon=False, bbox_to_anchor=(0.5, -0.32))

ps.caption(fig, "Figure 12. (A) Across the 8-category confirmatory socioemotional family (Bales IPA "
    "positive/negative quadrants + act4teams-full positive/negative facets), reorganization events are "
    "accompanied by a positive, not a negative, socioemotional signature: agreement, positive socio-"
    "emotional acts, and solidarity rise significantly (BH-FDR q<.001-.0003); disagreement/tension/"
    "antagonism do not survive FDR. (B) The positive signature is a sharp spike coincident with the "
    "event itself (rises pre→onset, falls onset→post, both p<.02 by circular-shift null) - not a "
    "before-the-fact lubricant nor an after-the-fact repair; the negative composite rises into the "
    "event but does not significantly recede afterward. Two attempted coding-free lexical markers "
    "(typed laughter conventions, exclamation density) returned null data in this ASR-transcribed, "
    "spoken corpus and are not plotted (see RESULTS.md).", y=-0.06)
fig.tight_layout(rect=[0, 0.05, 1, 1])
ps.save(fig, "fig_paper_S12_socioemotional")
