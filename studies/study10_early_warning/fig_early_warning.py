"""Figure: early-warning signature. Panel A (two stacked mini-plots) = time-locked entropy_g / det_g
trajectories over [-60,0)s before onset, event vs matched baseline, mean +/- meeting-clustered
bootstrap 95% CI. Panel B = ROC curves (FULL vs BEHAVIORAL model), leave-one-meeting-out CV, with AUC."""
import glob, os, re
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

COORD = "#2E7D8C"; DELIB = "#d95f02"; INK = "#1f2937"; NEUTRAL = "#6b7280"; GRID = "#e5e7eb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": "#9aa0a6", "axes.linewidth": .8,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.labelsize": 10.5,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .7, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "figure.dpi": 150, "savefig.dpi": 600, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "svg.fonttype": "none"})

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
BASE = os.path.dirname(__file__) + "/.."
D = pd.read_csv(f"{BASE}/data/preevent_features.csv")  # W=60, gives mid/onset_s/label
W = 60
rng = np.random.default_rng(10)

# --- reconstruct time-locked entropy_g/det_g trajectories for every (mid, onset_s, label) ---
cache = {}
traj_rows = []
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    sub = D[D.mid == mid]
    if not len(sub):
        continue
    g = pd.read_csv(f)
    sec = g.second.to_numpy(float); ent = g.entropy_g.to_numpy(float); det = g.det_g.to_numpy(float)
    for _, r in sub.iterrows():
        lo, hi = r.onset_s - W, r.onset_s
        m = (sec >= lo) & (sec < hi)
        if m.sum() < W * 0.7:
            continue
        t_rel = np.round(sec[m] - r.onset_s).astype(int)  # -60..-1
        for tr, e, d_ in zip(t_rel, ent[m], det[m]):
            traj_rows.append(dict(mid=mid, event_id=r.event_id, label=r.label, t_rel=tr, entropy=e, det=d_))
TRAJ = pd.DataFrame(traj_rows)

def clustered_mean_ci(sub, valcol, n_boot=500):
    """Mean +/- 95% CI at each t_rel, bootstrapped by meeting (cluster-aware).
    Precomputes a (meeting x t_rel) mean table once, then each bootstrap draw is pure numpy indexing
    (no per-iteration pandas concat/groupby) - orders of magnitude faster than the naive version."""
    t_rels = np.sort(sub.t_rel.unique())
    mids = np.sort(sub.mid.unique())
    # per-meeting, per-t_rel mean table (rows=meetings, cols=t_rels), NaN where a meeting lacks that t_rel
    tab = sub.groupby(["mid", "t_rel"])[valcol].mean().unstack("t_rel").reindex(index=mids, columns=t_rels)
    M = tab.to_numpy(dtype=float)  # (n_mids, n_trels)
    overall_mean = np.nanmean(M, axis=0)  # simple across-meeting mean (unweighted by event count, cluster-fair)
    n_mid = len(mids)
    boots = np.empty((n_boot, len(t_rels)))
    for b in range(n_boot):
        pick = rng.integers(0, n_mid, size=n_mid)
        boots[b] = np.nanmean(M[pick], axis=0)
    lo = np.nanpercentile(boots, 2.5, axis=0); hi = np.nanpercentile(boots, 97.5, axis=0)
    return t_rels, overall_mean, lo, hi

fig = plt.figure(figsize=(15, 5.6))
gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1], hspace=.15)
axA1 = fig.add_subplot(gs[0, 0]); axA2 = fig.add_subplot(gs[1, 0], sharex=axA1)
axB = fig.add_subplot(gs[:, 1])

for label, color, name in [(1, DELIB, "event-pre"), (0, COORD, "matched baseline")]:
    sub = TRAJ[TRAJ.label == label]
    t, m, lo, hi = clustered_mean_ci(sub, "entropy")
    axA1.plot(t, m, color=color, lw=2, label=name)
    axA1.fill_between(t, lo, hi, color=color, alpha=.18, lw=0)
    t, m, lo, hi = clustered_mean_ci(sub, "det")
    axA2.plot(t, m, color=color, lw=2)
    axA2.fill_between(t, lo, hi, color=color, alpha=.18, lw=0)
axA1.axvline(0, color=INK, lw=.8, ls=":"); axA2.axvline(0, color=INK, lw=.8, ls=":")
axA1.set_ylabel("entropy_g"); axA2.set_ylabel("det_g"); axA2.set_xlabel("seconds before event onset (0 = onset)")
axA1.set_title("A  Time-locked trajectories, [-60,0)s before onset", loc="left", fontsize=10.5)
axA1.legend(fontsize=8.5, loc="upper left")
axA1.text(.5, 1.13, "mean ± meeting-bootstrap 95% CI", transform=axA1.transAxes, ha="center",
          fontsize=8.5, style="italic", color=NEUTRAL)
plt.setp(axA1.get_xticklabels(), visible=False)

# --- Panel B: ROC curves ---
npz = np.load(f"{BASE}/data/roc_curves.npz")
auc_df = pd.read_csv(f"{BASE}/data/cv_auc_results.csv")
for key, lookup, color, lbl in [("full", "FULL", INK, "FULL (incl. entropy/%DET slope)"),
                                 ("behav", "BEHAVIORAL", DELIB, "BEHAVIORAL only (turn-taking/text)")]:
    fpr, tpr = npz[f"fpr_{key}"], npz[f"tpr_{key}"]
    row = auc_df[auc_df.label == lookup].iloc[0]
    axB.plot(fpr, tpr, color=color, lw=2.2,
              label=f"{lbl}\nAUC={row.auc:.2f} [{row.ci_lo:.2f},{row.ci_hi:.2f}]")
axB.plot([0, 1], [0, 1], "--", color=NEUTRAL, lw=1)
axB.set_xlabel("false positive rate"); axB.set_ylabel("true positive rate")
axB.set_title("B  Event-pre vs baseline discriminability\n(leave-one-meeting-out CV, 34 folds)", loc="left", fontsize=10.5)
axB.legend(fontsize=8.3, loc="lower right")
axB.set_aspect("equal")

fig.suptitle("Study 10 — A real but modest early-warning signature: population-level regularity, not a reliable single-event alarm",
             fontsize=12, fontweight="bold", x=.01, ha="left", y=1.03)
fig.text(0.5, -0.04,
         "Figure 10. (A) Entropy rises / %DET falls approaching an event vs a flat matched baseline — expected in part by "
         "construction (approaching a local extremum). (B) Leave-one-meeting-out discriminability is modest even restricting "
         "to turn-taking/text features with no mechanical tie to the metric (AUC≈0.66) — a real, population-level regularity "
         "(meeting-level paired effects are large, rank-biserial ≈.9-1.0) but not a reliable single-event alarm; most individual "
         "events show no detectable precursor by a 1-SD criterion.",
         ha="center", va="top", fontsize=8.1, color=NEUTRAL, style="italic", wrap=True)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
for ext in ("png", "pdf", "svg"):
    fig.savefig(f"{BASE}/fig_early_warning.{ext}", bbox_inches="tight", facecolor="white",
                dpi=600 if ext == "png" else None)
print("wrote fig_early_warning.{png,pdf,svg}")
