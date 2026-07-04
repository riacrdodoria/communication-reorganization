"""T1 (statistics) - Paired comparison: event-pre windows vs their matched baselines, per meeting,
across the 6 features. Per meeting: mean(event feature) - mean(matched-baseline feature); Wilcoxon
signed-rank across the 34 meeting-level differences; BH-FDR across the 6 features. Effect size =
matched-pairs rank-biserial correlation. Runs for a given (window_s, csv_path) pair so T4 can reuse it
for the 30/90s sensitivity files."""
import sys, os
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

FEATURES = ["entropy_slope", "det_slope", "switch_rate", "turnlen_trend", "question_density", "gap_trend"]
NICE = {"entropy_slope": "entropy slope (rising = more disordered)",
        "det_slope": "%DET slope (falling = less recurrent)",
        "switch_rate": "speaker-switch rate (per min)",
        "turnlen_trend": "turn-length trend (word count)",
        "question_density": "question density (share of turns with '?')",
        "gap_trend": "inter-utterance silence-gap trend"}


def rank_biserial(x, y):
    """Matched-pairs rank-biserial correlation for Wilcoxon (x=event, y=baseline paired means)."""
    d = np.asarray(x) - np.asarray(y)
    d = d[d != 0]
    if len(d) == 0:
        return np.nan
    r = pd.Series(np.abs(d)).rank().to_numpy()
    pos = r[d > 0].sum(); neg = r[d < 0].sum()
    return (pos - neg) / (pos + neg)


def run(csv_path, label):
    D = pd.read_csv(csv_path)
    print("=" * 90, f"\nPaired event-pre vs matched-baseline, window={D.window_s.iloc[0]}s  [{label}]\n" + "=" * 90)
    rows = []
    for feat in FEATURES:
        per_mtg = []
        for mid, g in D.groupby("mid"):
            ev = g[g.label == 1][feat].dropna()
            bl = g[g.label == 0][feat].dropna()
            if len(ev) < 3 or len(bl) < 3:
                continue
            per_mtg.append(dict(mid=mid, ev_mean=ev.mean(), bl_mean=bl.mean()))
        P = pd.DataFrame(per_mtg)
        if len(P) < 8:
            rows.append(dict(feature=feat, n_meetings=len(P), diff_mean=np.nan, p=np.nan, rb=np.nan))
            continue
        try:
            stat, p = wilcoxon(P.ev_mean, P.bl_mean)
        except Exception:
            p = 1.0
        rb = rank_biserial(P.ev_mean, P.bl_mean)
        diff = (P.ev_mean - P.bl_mean).mean()
        rows.append(dict(feature=feat, n_meetings=len(P), diff_mean=diff, ev_mean=P.ev_mean.mean(),
                          bl_mean=P.bl_mean.mean(), p=p, rank_biserial=rb))
    R = pd.DataFrame(rows)
    ok = R.p.notna()
    R.loc[ok, "q"] = multipletests(R.loc[ok, "p"], method="fdr_bh")[1]
    R["sig"] = R.get("q", pd.Series(np.nan, index=R.index)).apply(
        lambda q: "***" if q < .001 else "**" if q < .01 else "*" if q < .05 else "" if pd.notna(q) else "")
    R["label"] = label
    print(R.round(4).to_string(index=False))
    return R


if __name__ == "__main__":
    BASE = os.path.dirname(__file__) + "/.."
    R60 = run(f"{BASE}/data/preevent_features.csv", "W=60 (primary)")
    R60.to_csv(f"{BASE}/data/paired_tests_w60.csv", index=False)
    print("\nwrote paired_tests_w60.csv")

    # T4 - timescale sensitivity
    R30 = run(f"{BASE}/data/preevent_features_w30.csv", "W=30 (sensitivity)")
    R30.to_csv(f"{BASE}/data/paired_tests_w30.csv", index=False)
    R90 = run(f"{BASE}/data/preevent_features_w90.csv", "W=90 (sensitivity)")
    R90.to_csv(f"{BASE}/data/paired_tests_w90.csv", index=False)
    ALL = pd.concat([R60, R30, R90], ignore_index=True)
    ALL.to_csv(f"{BASE}/data/paired_tests_all_windows.csv", index=False)
    print("\n" + "=" * 90, "\nTimescale sensitivity summary (rank-biserial by window)\n" + "=" * 90)
    piv = ALL.pivot_table(index="feature", columns="label", values="rank_biserial")
    print(piv.round(3).to_string())
