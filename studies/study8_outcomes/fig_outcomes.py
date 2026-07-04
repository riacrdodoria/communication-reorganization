"""Figure: reorganization dynamics vs meeting-level outcomes (Study 8 / proposition P6).
Panel A-C: the direct adaptive-function proxy (reorg_event_rate) against all three outcomes - all null.
Panel D: the single strongest UNADJUSTED correlate (baseline_entropy vs issue resolution) - flagged as
not surviving BH-FDR, shown for transparency/future-work, not as a finding."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

COORD = "#2E7D8C"; DELIB = "#d95f02"; INK = "#1f2937"; NEUTRAL = "#6b7280"; GRID = "#e5e7eb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": "#9aa0a6", "axes.linewidth": .8,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.labelsize": 10.5,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .7, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
    "figure.dpi": 150, "savefig.dpi": 600, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "svg.fonttype": "none"})

BASE = "/Users/ricardodoria/lsh-work/study8_outcomes"
D = pd.read_csv(f"{BASE}/data/analysis_panel.csv")

def stars(q):
    return "***" if q < .001 else "**" if q < .01 else "*" if q < .05 else "n.s."

def panel(ax, x, y, xlabel, ylabel, color, title):
    sub = D[[x, y]].dropna()
    r, p = spearmanr(sub[x], sub[y])
    n = len(sub)
    ax.scatter(sub[x], sub[y], s=48, color=color, alpha=.8, edgecolor="white", lw=.6, zorder=3)
    z = np.polyfit(sub[x], sub[y], 1)
    xs = np.linspace(sub[x].min(), sub[x].max(), 50)
    ax.plot(xs, np.polyval(z, xs), "--", color=INK, lw=1.4, alpha=.6)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title, loc="left", fontsize=10)
    ax.text(.03, .96, f"Spearman ρ = {r:+.2f}, n = {n}\np = {p:.2f}", transform=ax.transAxes,
            va="top", ha="left", fontsize=8.6,
            bbox=dict(boxstyle="round,pad=0.35", fc="#f8fafc", ec="#cbd5e1", lw=.7))

fig, axes = plt.subplots(1, 4, figsize=(16, 4.4))
panel(axes[0], "reorg_event_rate", "rating_mean", "reorg-event rate (events/10 min)", "meeting rating (0-10)",
      COORD, "A  Reorg rate → rating")
panel(axes[1], "reorg_event_rate", "todo_completion_rate", "reorg-event rate (events/10 min)",
      "to-do completion rate (%)", COORD, "B  Reorg rate → to-do completion")
panel(axes[2], "reorg_event_rate", "issue_resolution_rate_same_meeting", "reorg-event rate (events/10 min)",
      "IDS issue resolution rate (%)", COORD, "C  Reorg rate → issue resolution")
panel(axes[3], "baseline_entropy", "issue_resolution_rate_same_meeting", "baseline entropy (resting)",
      "IDS issue resolution rate (%)", DELIB, "D  Strongest unadjusted correlate\n(q = .22, does not survive FDR)")

fig.suptitle("Study 8 — Reorganization dynamics do not predict meeting-level outcomes at this sample size (n = 29-34)",
             fontsize=12.5, fontweight="bold", x=.01, ha="left", y=1.04)
fig.text(0.5, -0.06,
         "Figure 8. (A-C) The direct adaptive-function proxy (reorg-event rate) is null across all three outcomes "
         "(all |ρ| < .15, n.s.). (D) The single largest unadjusted correlation in the whole predictor x outcome grid "
         "(14 predictors x 3 outcomes, BH-FDR within each outcome family) — flagged for transparency and future work, "
         "not reported as a finding: it does not survive correction (q = .22).",
         ha="center", va="top", fontsize=8.3, color=NEUTRAL, style="italic", wrap=True)
fig.tight_layout(rect=[0, 0.04, 1, 0.96])
for ext in ("png", "pdf", "svg"):
    fig.savefig(f"{BASE}/../fig_outcomes_scatter.{ext}" if False else f"{BASE}/fig_outcomes_scatter.{ext}",
                bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("wrote fig_outcomes_scatter.{png,pdf,svg}")
