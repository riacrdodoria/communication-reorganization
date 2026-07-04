"""T3 - Meso forecasting: does the first half of a meeting predict its own second half?

First-half features (baseline entropy = median entropy_g, event rate = events/10min, %DET median),
all computed ONLY from seconds < meeting midpoint -> second-half event rate (seconds >= midpoint).
Spearman, per team + pooled. Then: first-half features -> Study 8 meeting rating (rating_mean),
reported alongside (not instead of) Study 8's own whole-meeting predictors, since this is a distinct,
narrower question (does knowing only the FIRST HALF forecast the outcome, before the meeting is even
over) rather than Study 8's whole-meeting predictor x outcome grid."""
import glob, os, re
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
BASE = os.path.dirname(__file__) + "/.."
TCRIT = 2.33


def parse_date_team(mid):
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})(startup_[ab])", mid)
    y, mo, d, team = m.groups()
    return int(f"{y}{mo}{d}"), team


rows = []
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    date, team = parse_date_team(mid)
    g = pd.read_csv(f)
    sec = g.second.to_numpy(float); ent = g.entropy_g.to_numpy(float)
    det = g.det_g.to_numpy(float); rm = g.rmse_g.to_numpy(float)
    ok = np.isfinite(rm)
    if ok.sum() < 60:
        continue
    rmean, rsd = np.nanmean(rm[ok]), np.nanstd(rm[ok])  # meeting-internal threshold, both halves included
    is_event = rm > rmean + TCRIT * rsd
    mid_t = (np.nanmin(sec) + np.nanmax(sec)) / 2
    h1 = sec < mid_t; h2 = sec >= mid_t
    dur1_min = (mid_t - np.nanmin(sec)) / 60; dur2_min = (np.nanmax(sec) - mid_t) / 60
    rows.append(dict(
        mid=mid, team=team, date=date,
        h1_baseline_entropy=np.nanmedian(ent[h1]), h1_det_median=np.nanmedian(det[h1]),
        h1_event_rate=10 * np.nansum(is_event[h1 & ok]) / dur1_min if dur1_min > 0 else np.nan,
        h2_event_rate=10 * np.nansum(is_event[h2 & ok]) / dur2_min if dur2_min > 0 else np.nan,
    ))
D = pd.DataFrame(rows).sort_values(["team", "date"])
D["week"] = D.groupby("team").cumcount()
D.to_csv(f"{BASE}/data/meso_halves.csv", index=False)

print("=" * 90, "\nT3a - First-half features -> second-half event rate (Spearman)\n" + "=" * 90)
FEATS = ["h1_baseline_entropy", "h1_det_median", "h1_event_rate"]
rows2 = []
for feat in FEATS:
    for team, g in D.groupby("team"):
        sub = g[[feat, "h2_event_rate"]].dropna()
        if len(sub) >= 8:
            r, p = spearmanr(sub[feat], sub["h2_event_rate"])
        else:
            r, p = np.nan, np.nan
        rows2.append(dict(feature=feat, team=team, n=len(sub), rho=r, p=p))
        print(f"{feat:22s} {team:10s}: n={len(sub)}  rho={r:+.3f}  p={p:.3f}" if not np.isnan(r) else f"{feat} {team}: insufficient")
    sub = D[[feat, "h2_event_rate"]].dropna()
    r, p = spearmanr(sub[feat], sub["h2_event_rate"])
    rows2.append(dict(feature=feat, team="pooled", n=len(sub), rho=r, p=p))
    print(f"{feat:22s} {'pooled':10s}: n={len(sub)}  rho={r:+.3f}  p={p:.3f}")
R2 = pd.DataFrame(rows2)
pooled_mask = R2.team == "pooled"
R2.loc[pooled_mask, "q"] = multipletests(R2.loc[pooled_mask, "p"], method="fdr_bh")[1]
print("\nBH-FDR across the 3 pooled tests:")
print(R2[pooled_mask][["feature", "rho", "p", "q"]].round(4).to_string(index=False))
R2.to_csv(f"{BASE}/data/meso_h1_to_h2eventrate.csv", index=False)

print("\n" + "=" * 90, "\nT3b - First-half features -> Study 8 meeting rating (Spearman)\n" + "=" * 90)
S8 = pd.read_csv(os.path.expanduser("~/lsh-work/study8_outcomes/data/outcomes_per_meeting.csv"))
DR = D.merge(S8[["mid", "rating_mean", "todo_completion_rate", "issue_resolution_rate_same_meeting"]], on="mid", how="inner")
rows3 = []
for feat in FEATS:
    for outcome in ["rating_mean", "todo_completion_rate", "issue_resolution_rate_same_meeting"]:
        sub = DR[[feat, outcome]].dropna()
        if len(sub) >= 8:
            r, p = spearmanr(sub[feat], sub[outcome])
        else:
            r, p = np.nan, np.nan
        rows3.append(dict(feature=feat, outcome=outcome, n=len(sub), rho=r, p=p))
        print(f"{feat:22s} -> {outcome:32s}: n={len(sub)}  rho={r:+.3f}  p={p:.3f}" if not np.isnan(r) else "insufficient")
R3 = pd.DataFrame(rows3)
ok = R3.p.notna()
R3.loc[ok, "q"] = multipletests(R3.loc[ok, "p"], method="fdr_bh")[1]
print("\nBH-FDR across all 9 first-half-feature x outcome tests:")
print(R3[["feature", "outcome", "rho", "p", "q"]].round(4).to_string(index=False))
R3.to_csv(f"{BASE}/data/meso_h1_to_outcomes.csv", index=False)
print(f"\n(n meetings with S8 outcomes merged: {len(DR)}/{len(D)})")
print("\nwrote meso_halves.csv, meso_h1_to_h2eventrate.csv, meso_h1_to_outcomes.csv")
