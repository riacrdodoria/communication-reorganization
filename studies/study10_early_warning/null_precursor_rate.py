"""T4 (continued) - What fraction of events show NO detectable precursor?

For the entropy_slope feature (the theoretically central, most interpretable signal): for each event,
compare its pre-event entropy_slope to that SAME MEETING's own baseline entropy_slope distribution
(mean+SD, so the comparison is meeting-internal, not pooled across meetings - no cross-meeting leakage).
An event's precursor is called 'not detectable' if its entropy_slope falls within +/-1 SD of that
meeting's baseline mean (i.e., indistinguishable from an ordinary, non-event stretch of the meeting).
Repeated for switch_rate (the strongest single behavioral feature) for comparison.

This connects honestly to the critical-transitions literature: some reorganizations may be genuinely
abrupt (no detectable ramp-up), rather than every reorganization having graded early-warning signs."""
import os
import numpy as np, pandas as pd

BASE = os.path.dirname(__file__) + "/.."
D = pd.read_csv(f"{BASE}/data/preevent_features.csv")

rows = []
for feat in ["entropy_slope", "switch_rate"]:
    n_total = 0; n_no_precursor = 0
    per_event_flag = []
    for mid, g in D.groupby("mid"):
        bl = g[g.label == 0][feat].dropna()
        ev = g[g.label == 1][[feat, "event_id"]].dropna(subset=[feat])
        if len(bl) < 5 or len(ev) == 0:
            continue
        mu, sd = bl.mean(), bl.std()
        if not sd or sd == 0:
            continue
        for _, r in ev.iterrows():
            n_total += 1
            no_prec = abs(r[feat] - mu) <= sd  # within 1 SD of this meeting's own baseline
            n_no_precursor += int(no_prec)
            per_event_flag.append(dict(mid=mid, event_id=r.event_id, feature=feat, no_precursor=no_prec))
    # 2026-09-05 (AUDIT S10 #2): the same criterion applied to the BASELINE windows themselves gives the
    # base rate of 'within 1 SD' (about 68% under normality). Report it next to the event rate.
    nb_tot = 0; nb_in = 0
    for mid, g in D.groupby("mid"):
        bl = g[g.label == 0][feat].dropna()
        if len(bl) < 5 or bl.std() == 0: continue
        nb_tot += len(bl); nb_in += int((np.abs(bl - bl.mean()) <= bl.std()).sum())
    rows.append(dict(feature=feat, n_events=n_total, n_no_precursor=n_no_precursor,
                      pct_no_precursor=100 * n_no_precursor / n_total if n_total else np.nan,
                      pct_baseline_within_1sd=100 * nb_in / nb_tot if nb_tot else np.nan,
                      excess_vs_baseline=(100 * n_no_precursor / n_total - 100 * nb_in / nb_tot) if (n_total and nb_tot) else np.nan))
    pd.DataFrame(per_event_flag).to_csv(f"{BASE}/data/no_precursor_flags_{feat}.csv", index=False)

R = pd.DataFrame(rows)
R.to_csv(f"{BASE}/data/no_precursor_summary.csv", index=False)
print("=" * 90, "\nT4 - Proportion of events with NO detectable precursor (within 1 SD of meeting's own baseline)\n" + "=" * 90)
print(R.round(1).to_string(index=False))
print("  (pct_baseline_within_1sd = base rate of the criterion on non-event windows; 'no precursor' is only informative relative to it)")

# how many events lack a precursor on BOTH features (genuinely abrupt on the two clearest signals)
e = pd.read_csv(f"{BASE}/data/no_precursor_flags_entropy_slope.csv")[["mid", "event_id", "no_precursor"]].rename(columns={"no_precursor": "no_prec_entropy"})
s = pd.read_csv(f"{BASE}/data/no_precursor_flags_switch_rate.csv")[["mid", "event_id", "no_precursor"]].rename(columns={"no_precursor": "no_prec_switch"})
both = e.merge(s, on=["mid", "event_id"], how="inner")
both["no_prec_both"] = both.no_prec_entropy & both.no_prec_switch
pct_both = 100 * both.no_prec_both.mean()
print(f"\nEvents with NO detectable precursor on BOTH entropy_slope AND switch_rate: "
      f"{both.no_prec_both.sum()}/{len(both)} ({pct_both:.1f}%) - candidates for genuinely abrupt transitions")
both.to_csv(f"{BASE}/data/no_precursor_both.csv", index=False)
