"""T3 - Statistical models: does reorganization predict meeting effectiveness?
- Spearman rho, predictor x outcome, pooled (Fisher-z 95% CI) + per-team descriptive; BH-FDR within
  each outcome family (across the 14 predictors).
- Mixed model: outcome ~ predictor + week + (1|team) (statsmodels MixedLM), same family/FDR logic on
  the predictor's fixed-effect p-value.
- Lag is by construction: todo_completion_rate(t) is checked in meeting t+1's to-do review, so
  predictors(t) -> todo_completion_rate(t) IS the lagged test; no extra step needed (documented).
- Nonlinearity probe: inverted-U (quadratic) for reorg_event_rate and pct_time_reorganizing vs each
  outcome (OLS with linear + quadratic term).
n is small (29-34) -> report effect sizes + 95% CI throughout; treat p/q as secondary.
"""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

BASE = "/Users/ricardodoria/lsh-work/study8_outcomes"
O = pd.read_csv(f"{BASE}/data/outcomes_per_meeting.csv")
P = pd.read_csv(f"{BASE}/data/predictors_per_meeting.csv")
D = O.merge(P.drop(columns=["team", "week", "date"]), on="mid", how="inner")
assert len(D) == 34, f"expected 34 merged rows, got {len(D)}"
D.to_csv(f"{BASE}/data/analysis_panel.csv", index=False)

PREDICTORS = ["baseline_entropy", "entropy_sd", "det_median", "pct_time_reorganizing",
              "reorg_event_rate", "mean_event_depth", "mean_event_peak_z", "boundary_alignment_pct",
              "ids_entropy", "ids_det", "ids_reorg_rate", "review_entropy", "review_det", "review_reorg_rate"]
OUTCOMES = ["rating_mean", "todo_completion_rate", "issue_resolution_rate_same_meeting"]
NICE_OUT = {"rating_mean": "Meeting rating (0-10, mean of spoken ratings)",
            "todo_completion_rate": "To-do completion rate (t -> t+1 check)",
            "issue_resolution_rate_same_meeting": "IDS issue resolution rate (same meeting)"}

def fisher_ci(r, n, alpha=.05):
    if n < 4 or abs(r) >= 1: return (np.nan, np.nan)
    z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    from scipy.stats import norm
    lo, hi = z - norm.ppf(1 - alpha / 2) * se, z + norm.ppf(1 - alpha / 2) * se
    return np.tanh(lo), np.tanh(hi)

# ---------- Spearman (pooled + per-team) ----------
print("=" * 100)
print("PART 1 - Spearman correlations, predictor x outcome (pooled n; 95% CI; BH-FDR within outcome family)")
print("=" * 100)
spearman_rows = []
for out in OUTCOMES:
    rows = []
    for pred in PREDICTORS:
        sub = D[[pred, out]].dropna()
        n = len(sub)
        if n < 8:
            rows.append(dict(predictor=pred, n=n, r=np.nan, lo=np.nan, hi=np.nan, p=np.nan)); continue
        r, p = spearmanr(sub[pred], sub[out])
        lo, hi = fisher_ci(r, n)
        rows.append(dict(predictor=pred, n=n, r=r, lo=lo, hi=hi, p=p))
    df = pd.DataFrame(rows)
    ok = df.p.notna()
    df.loc[ok, "q"] = multipletests(df.loc[ok, "p"], method="fdr_bh")[1]
    df["sig"] = df.q.apply(lambda q: "***" if q < .001 else "**" if q < .01 else "*" if q < .05 else "" if pd.notna(q) else "")
    df["outcome"] = out
    spearman_rows.append(df)
    print(f"\n--- outcome: {NICE_OUT[out]} ---")
    show = df[["predictor", "n", "r", "lo", "hi", "p", "q", "sig"]].sort_values("r", ascending=False)
    print(show.round(3).to_string(index=False))

SP = pd.concat(spearman_rows, ignore_index=True)
SP.to_csv(f"{BASE}/data/spearman_results.csv", index=False)

# per-team descriptive (small n, no FDR - exploratory only)
print("\n" + "=" * 100)
print("PART 1b - Per-team Spearman r (descriptive only; n~14-17 per team, underpowered)")
print("=" * 100)
team_rows = []
for out in OUTCOMES:
    for pred in PREDICTORS:
        row = dict(outcome=out, predictor=pred)
        for team, g in D.groupby("team"):
            sub = g[[pred, out]].dropna()
            if len(sub) >= 8:
                r, p = spearmanr(sub[pred], sub[out])
                row[f"{team}_r"] = r; row[f"{team}_n"] = len(sub)
            else:
                row[f"{team}_r"] = np.nan; row[f"{team}_n"] = len(sub)
        team_rows.append(row)
TEAM = pd.DataFrame(team_rows)
TEAM.to_csv(f"{BASE}/data/spearman_by_team.csv", index=False)
print(TEAM.round(2).to_string(index=False))

# ---------- Mixed model: outcome ~ predictor + week + (1|team) ----------
print("\n" + "=" * 100)
print("PART 2 - Mixed model: outcome ~ predictor (z-scored) + week + (1|team)")
print("=" * 100)
mm_rows = []
for out in OUTCOMES:
    rows = []
    for pred in PREDICTORS:
        sub = D[[pred, out, "week", "team"]].dropna().copy()
        n = len(sub)
        if n < 10 or sub[pred].std() == 0:
            rows.append(dict(predictor=pred, n=n, coef=np.nan, se=np.nan, p=np.nan)); continue
        sub["z"] = (sub[pred] - sub[pred].mean()) / sub[pred].std()
        try:
            md = smf.mixedlm(f"{out} ~ z + week", sub, groups=sub["team"])
            fit = md.fit(reml=False, method="lbfgs")
            coef, se, p = fit.params["z"], fit.bse["z"], fit.pvalues["z"]
        except Exception:
            coef, se, p = np.nan, np.nan, np.nan
        rows.append(dict(predictor=pred, n=n, coef=coef, se=se, p=p))
    df = pd.DataFrame(rows)
    ok = df.p.notna()
    if ok.sum():
        df.loc[ok, "q"] = multipletests(df.loc[ok, "p"], method="fdr_bh")[1]
    df["sig"] = df.get("q", pd.Series(np.nan, index=df.index)).apply(
        lambda q: "***" if q < .001 else "**" if q < .01 else "*" if q < .05 else "" if pd.notna(q) else "")
    df["outcome"] = out
    mm_rows.append(df)
    print(f"\n--- outcome: {NICE_OUT[out]} --- (coef = change in outcome per 1 SD of predictor)")
    print(df[["predictor", "n", "coef", "se", "p", "q", "sig"]].round(3).sort_values("coef", ascending=False).to_string(index=False))
MM = pd.concat(mm_rows, ignore_index=True)
MM.to_csv(f"{BASE}/data/mixedmodel_results.csv", index=False)

# ---------- Nonlinearity probe: inverted-U for reorg_event_rate and pct_time_reorganizing ----------
print("\n" + "=" * 100)
print("PART 3 - Nonlinearity probe (inverted-U): outcome ~ x + x^2, OLS")
print("=" * 100)
quad_rows = []
for out in OUTCOMES:
    for pred in ["reorg_event_rate", "pct_time_reorganizing"]:
        sub = D[[pred, out]].dropna().copy()
        n = len(sub)
        if n < 10:
            quad_rows.append(dict(outcome=out, predictor=pred, n=n)); continue
        x = sub[pred]; x = (x - x.mean()) / x.std()
        X = sm.add_constant(np.column_stack([x, x ** 2]))
        fit = sm.OLS(sub[out], X).fit()
        b1, b2 = fit.params[1], fit.params[2]
        p1, p2 = fit.pvalues[1], fit.pvalues[2]
        vertex_z = -b1 / (2 * b2) if b2 != 0 else np.nan
        shape = "inverted-U" if b2 < 0 else "U-shaped" if b2 > 0 else "flat"
        quad_rows.append(dict(outcome=out, predictor=pred, n=n, linear_b=b1, linear_p=p1,
                               quad_b=b2, quad_p=p2, shape=shape, vertex_z=vertex_z, r2=fit.rsquared))
QD = pd.DataFrame(quad_rows)
QD.to_csv(f"{BASE}/data/quadratic_results.csv", index=False)
print(QD.round(3).to_string(index=False))

print("\nAll T3 outputs written to study8_outcomes/data/: spearman_results.csv, spearman_by_team.csv,"
      " mixedmodel_results.csv, quadratic_results.csv, analysis_panel.csv")
