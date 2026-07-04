"""Follow-up - Which event TYPE has a detectable precursor and which does not?

Joins Study 9's event classification (TRANSITION / INTERIOR_HANDOFF / INTERIOR_OTHER - same detector,
same clustering, deterministic onset match, 909/909 join) onto Study 10's pre-event features and
no-precursor flags. Two questions:
  (a) Does the RATE of "no detectable precursor" differ by event class? (chi-square, 3 classes)
  (b) Does the MAGNITUDE of the precursor signal (entropy_slope, switch_rate) differ by class?
      (Kruskal-Wallis + pairwise Mann-Whitney with BH-FDR)
"""
import os
import numpy as np, pandas as pd
from scipy.stats import chi2_contingency, kruskal, mannwhitneyu
from statsmodels.stats.multitest import multipletests

LSH = os.path.expanduser("~/lsh-work")
BASE = os.path.dirname(__file__) + "/.."
CLASSES = ["TRANSITION", "INTERIOR_HANDOFF", "INTERIOR_OTHER"]

E9 = pd.read_csv(f"{LSH}/study9_initiators/data/events_initiators.csv")[["mid", "event_onset_s", "event_class"]]
P10 = pd.read_csv(f"{BASE}/data/preevent_features.csv")
EV = P10[P10.label == 1].merge(E9, left_on=["mid", "onset_s"], right_on=["mid", "event_onset_s"], how="left")
assert EV.event_class.notna().all(), "unmatched events found"

npe = pd.read_csv(f"{BASE}/data/no_precursor_flags_entropy_slope.csv")
nps = pd.read_csv(f"{BASE}/data/no_precursor_flags_switch_rate.csv")
EV = EV.merge(npe[["mid", "event_id", "no_precursor"]].rename(columns={"no_precursor": "no_prec_entropy"}),
              on=["mid", "event_id"], how="left")
EV = EV.merge(nps[["mid", "event_id", "no_precursor"]].rename(columns={"no_precursor": "no_prec_switch"}),
              on=["mid", "event_id"], how="left")
EV["no_prec_both"] = EV.no_prec_entropy & EV.no_prec_switch
EV.to_csv(f"{BASE}/data/precursor_by_class.csv", index=False)

print("=" * 90, "\n(a) No-precursor RATE by event class\n" + "=" * 90)
rows = []
for flag, label in [("no_prec_entropy", "entropy_slope"), ("no_prec_switch", "switch_rate"), ("no_prec_both", "both")]:
    sub = EV.dropna(subset=[flag])
    tab = sub.groupby("event_class")[flag].agg(["sum", "count"])
    tab["pct_no_precursor"] = 100 * tab["sum"] / tab["count"]
    tab = tab.reindex(CLASSES)
    ct = pd.crosstab(sub.event_class, sub[flag])
    chi2, p, dof, exp = chi2_contingency(ct)
    print(f"\n--- {label} ---")
    print(tab.round(1).to_string())
    print(f"chi2({dof})={chi2:.2f}  p={p:.4g}  min_expected={exp.min():.1f}")
    for cls in CLASSES:
        rows.append(dict(feature=label, event_class=cls, pct_no_precursor=tab.loc[cls, "pct_no_precursor"],
                          n=int(tab.loc[cls, "count"]), chi2=chi2, chi2_p=p))
pd.DataFrame(rows).to_csv(f"{BASE}/data/no_precursor_rate_by_class.csv", index=False)

print("\n" + "=" * 90, "\n(b) MAGNITUDE of precursor signal by event class (Kruskal-Wallis + pairwise MWU)\n" + "=" * 90)
mag_rows = []
for feat in ["entropy_slope", "det_slope", "switch_rate", "turnlen_trend", "question_density"]:
    groups = [EV[EV.event_class == c][feat].dropna() for c in CLASSES]
    H, p = kruskal(*groups)
    means = {c: EV[EV.event_class == c][feat].mean() for c in CLASSES}
    print(f"\n--- {feat} ---  means: " + ", ".join(f"{c}={means[c]:.2f}" for c in CLASSES))
    print(f"Kruskal-Wallis H={H:.2f}  p={p:.4g}")
    pair_rows = []
    for i in range(len(CLASSES)):
        for j in range(i + 1, len(CLASSES)):
            a, b = CLASSES[i], CLASSES[j]
            ga, gb = EV[EV.event_class == a][feat].dropna(), EV[EV.event_class == b][feat].dropna()
            U, pw = mannwhitneyu(ga, gb)
            pair_rows.append(dict(feature=feat, a=a, b=b, mean_a=ga.mean(), mean_b=gb.mean(), p=pw))
    PW = pd.DataFrame(pair_rows)
    PW["q"] = multipletests(PW.p, method="fdr_bh")[1]
    PW["sig"] = PW.q.apply(lambda q: "***" if q < .001 else "**" if q < .01 else "*" if q < .05 else "")
    print(PW.round(4).to_string(index=False))
    mag_rows.append(dict(feature=feat, kruskal_H=H, kruskal_p=p, **{f"mean_{c}": means[c] for c in CLASSES}))
    PW.to_csv(f"{BASE}/data/precursor_magnitude_pairwise_{feat}.csv", index=False)
pd.DataFrame(mag_rows).to_csv(f"{BASE}/data/precursor_magnitude_by_class.csv", index=False)
print("\nwrote precursor_by_class.csv, no_precursor_rate_by_class.csv, precursor_magnitude_by_class.csv, "
      "precursor_magnitude_pairwise_<feature>.csv")
