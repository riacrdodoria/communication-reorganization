"""T2 - Build predictors_per_meeting.csv by REUSING existing Study 2/6/7 pipeline outputs.
Does not recompute entropy_g/det_g/rmse_g (the metric engine) or the reorg-event/boundary definitions
already established (rmse_g > mean+2.33 SD; +/-30s boundary zone). Only aggregates already-computed
per-second series into per-meeting descriptive predictors, and joins already-computed meeting-level
summaries (Study 7's decomposition/depth panels, Study 6's L10 stage metrics)."""
import glob, os, numpy as np, pandas as pd

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
OUT = os.path.expanduser("~/lsh-work/study8_outcomes/data/predictors_per_meeting.csv")
TCRIT = 2.33  # same threshold used throughout Studies 2/6/7 for a reorg event

# --- 1. Per-second descriptive aggregates (median/SD of already-computed entropy_g/det_g; event share) ---
rows = []
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    g = pd.read_csv(f)
    ent = g["entropy_g"].to_numpy(float)
    det = g["det_g"].to_numpy(float)
    rm = g["rmse_g"].to_numpy(float)
    ok = np.isfinite(rm)
    if ok.sum() < 60:
        continue
    thr = np.nanmean(rm[ok]) + TCRIT * np.nanstd(rm[ok])
    pct_time_reorganizing = 100 * np.mean(rm[ok] > thr)
    rows.append(dict(
        mid=mid,
        baseline_entropy=np.nanmedian(ent),
        entropy_sd=np.nanstd(ent),
        det_median=np.nanmedian(det),
        pct_time_reorganizing=pct_time_reorganizing,
    ))
DESC = pd.DataFrame(rows)

# --- 2. Reuse Study 7's per-meeting event decomposition/depth panels (no recompute) ---
DEP = pd.read_csv(f"{LSH}/reorg_depth_longitudinal_panel.csv")
DEP["n_events"] = DEP.BORDER_n.fillna(0) + DEP.INTERIOR_n.fillna(0)
w_ent_exc = (DEP.BORDER_ent_exc.fillna(0) * DEP.BORDER_n.fillna(0) +
             DEP.INTERIOR_ent_exc.fillna(0) * DEP.INTERIOR_n.fillna(0)) / DEP.n_events.replace(0, np.nan)
w_peak_z = (DEP.BORDER_peak_z.fillna(0) * DEP.BORDER_n.fillna(0) +
            DEP.INTERIOR_peak_z.fillna(0) * DEP.INTERIOR_n.fillna(0)) / DEP.n_events.replace(0, np.nan)
DEP["mean_event_depth"] = w_ent_exc      # entropy points above the meeting's own baseline
DEP["mean_event_peak_z"] = w_peak_z      # same, in within-meeting SD units (robustness alt.)
DEP = DEP[["mid", "team", "week", "date", "n_events", "mean_event_depth", "mean_event_peak_z"]]

# --- 3. Reuse Study 7's boundary-alignment / transition-share decomposition (no recompute) ---
BND = pd.read_csv(f"{LSH}/reorg_decomposition_union_W30.csv")[["mid", "pct_tr"]]
BND = BND.rename(columns={"pct_tr": "boundary_alignment_pct"})

# --- 4. Meeting duration + boundary count (reuse Study 7 longitudinal panel) ---
DUR = pd.read_csv(f"{LSH}/reorg_longitudinal_panel.csv")[["mid", "dur_min", "n_bounds"]]

# --- 5. Reuse Study 6's L10 stage metrics for IDS-only / review-only predictors ---
L10 = pd.read_csv(f"{LSH}/l10_stage_metrics.csv")
REVIEW = {"scorecard", "rock_review", "todo"}
def stage_agg(g, mask, prefix):
    s = g[mask]
    if not len(s) or s.secs.sum() == 0:
        return {f"{prefix}_entropy": np.nan, f"{prefix}_det": np.nan, f"{prefix}_reorg_rate": np.nan}
    w = s.secs
    return {f"{prefix}_entropy": np.average(s.entropy, weights=w),
            f"{prefix}_det": np.average(s.det, weights=w),
            f"{prefix}_reorg_rate": np.average(s.reorg_rate, weights=w)}
stage_rows = []
for mid, g in L10.groupby("mid"):
    row = {"mid": mid}
    row.update(stage_agg(g, g.stage == "ids", "ids"))
    row.update(stage_agg(g, g.stage.isin(REVIEW), "review"))
    stage_rows.append(row)
STAGE = pd.DataFrame(stage_rows)

# --- Assemble ---
P = DESC.merge(DEP, on="mid", how="left") \
        .merge(BND, on="mid", how="left") \
        .merge(DUR, on="mid", how="left") \
        .merge(STAGE, on="mid", how="left")
P["reorg_event_rate"] = 10 * P.n_events / P.dur_min  # events per 10 minutes

cols = ["mid", "team", "week", "date", "dur_min", "baseline_entropy", "entropy_sd", "det_median",
        "pct_time_reorganizing", "n_events", "reorg_event_rate", "mean_event_depth", "mean_event_peak_z",
        "boundary_alignment_pct", "n_bounds", "ids_entropy", "ids_det", "ids_reorg_rate",
        "review_entropy", "review_det", "review_reorg_rate"]
P = P[cols].sort_values(["team", "week"])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
P.to_csv(OUT, index=False)
print(f"wrote {OUT}  ({len(P)} meetings, {P.team.nunique()} teams)")
print(P.describe().T[["count", "mean", "std", "min", "max"]].round(2).to_string())
