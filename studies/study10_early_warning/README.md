# Study 10 — Anticipating reorganization (early-warning signatures)

## Rationale and gap
Wiltshire (2026, *Small Group Research*) closes by calling the field to move beyond post hoc
description toward anticipating coordination breakdowns and supporting adaptive teamwork in real
time. This study answers that call inside our corpus, as a **feasibility probe** — not a production
classifier. Two questions: (1) **micro** — do the 30–90 s preceding a reorganization event carry a
detectable signature relative to matched non-event baselines? (2) **meso** — do first-half-of-meeting
dynamics predict the meeting's own second half and its Study-8 outcome rating?

## Method
913 reorganization events (34 meetings, bot-cleaned corpus; same detector as Studies 2/6/7/9: RMSE >
mean+2.33 SD, 8 s gap clustering). Six features over the **[−60, 0) s window before onset** (30/90 s reruns for
sensitivity): `entropy_slope`, `det_slope` (mechanically tied to the metric itself — see caveat below),
and four independent turn-taking/text features with **no mechanical link** to how the reorganization
metric is computed — `switch_rate`, `turnlen_trend`, `question_density`, `gap_trend`. Each event is
matched to 3 seeded baseline windows (same L10 stage where possible, ≥90 s from every event onset in
that meeting). Statistics: paired per-meeting Wilcoxon + BH-FDR + matched-pairs rank-biserial effect
size (T1); leave-one-meeting-out logistic-regression CV with meeting-bootstrap AUC CI (T2); Spearman
first-half → second-half/outcome with BH-FDR (T3); timescale sensitivity + a "no detectable precursor"
rate (T4). Full leakage audit in `RESULTS.md`.

## Results
- **A real, mechanism-independent precursor signature exists.** Restricting to the four
  non-circular behavioral features, event-pre windows differ from matched baselines on 3/4 (all but
  `gap_trend`), with large, meeting-consistent effects (rank-biserial ≈ .87–1.00, stable across 30–90 s
  windows): **rising speaker-switch rate, shortening/choppier turns, and *fewer* questions** precede
  reorganization. (`entropy_slope`/`det_slope` also show the expected pattern, but this is largely
  definitional — a window ending just before a local entropy peak/%DET valley mechanically tends to
  show that trend — and is not treated as an independent discovery.)
- **The same signal is only modestly discriminable at the single-event level.** A leave-one-meeting-out
  classifier using only the four non-circular features reaches **AUC = 0.66 [95% CI 0.62, 0.70]**
  (full model incl. entropy/%DET slope: AUC = 0.68 [0.65, 0.72]). Real, above chance, but modest — the
  central honest tension of this study: near-ceiling *meeting-level* consistency coexists with modest
  *event-level* discriminability.
- **"No detectable precursor" must be read against the criterion's base rate (corrected 2026-09-05).**
  By the meeting-internal ±1 SD criterion, 71.9 % of events show no `entropy_slope` precursor and 50.7 %
  none on `switch_rate`; 34.0 % none on either. But the same criterion classifies **69 %** of ordinary
  baseline windows as "within 1 SD" (`results/no_precursor_summary.csv`, column
  `pct_baseline_within_1sd`). The `entropy_slope` figure is therefore the base rate (+2.9 points) and
  says nothing about abruptness; only `switch_rate` (−18 points below base rate) carries information,
  and it says that half of the events *are* preceded by a detectable switching ramp. The earlier
  reading of these percentages as evidence for abrupt transitions is withdrawn.
- **No within-meeting "budget" (corrected 2026-09-05).** An earlier version reported that a meeting's
  first-half reorganization rate negatively predicts its second half (ρ = −0.64) and read it as
  self-regulation. That association is produced by the event threshold, which is computed from the whole
  meeting: a busy first half raises the threshold for the second half. Under an **online** threshold
  (first-half statistics only) ρ = +0.03 (p = .86); under a single global threshold ρ = +0.38; and a
  circular-shift null that keeps the per-meeting threshold reproduces the negative value (null mean
  −0.70, 95 % [−0.80, −0.56]; `results/meso_budget_sensitivity.csv`). First-half dynamics do **not**
  forecast Study 8's outcomes (0/9 tests survive BH-FDR), consistent with Study 8's own null.
- **Which event *type* is anticipatable differs by channel** (joining Study 9's event classification):
  topic/agenda TRANSITIONs are anticipated mainly through rising multi-party switching (lowest
  no-precursor rate on `switch_rate`; χ²(2) = 25.7, p < .001; mean switch rate 6.7 vs 5.3 / 5.1); interior floor handoffs show the
  cleanest entropy/%DET ramp of the three classes; and **INTERIOR_OTHER — the diffuse residual interior
  category — is the least anticipatable on nearly every measure** (flattest entropy/%DET ramp, lowest
  switch-rate, highest no-precursor rate, even an inverted turn-length signature), the closest thing in
  this corpus to a genuinely abrupt reorganization.

Full statistics, the complete leakage audit, and honest interpretation: `RESULTS.md`.

## Honest scope
- 2 teams, 34 meetings — replication, not generalization, as throughout this program.
- A single fixed regularization default is used for the classifier (no tuning), by design, given the
  guardrail against AUC-chasing at this sample size.
- The event/RMSE detection threshold is computed per meeting from that meeting's own full RMSE series
  (established convention throughout this program). This is appropriate for the event-level analyses
  (T1, T2), but it makes any *within-meeting* comparison of event rates across time dependent by
  construction — which is what produced the withdrawn "budget" result; the online threshold is the
  right instrument for such comparisons and is now reported alongside.
- The "no detectable precursor" percentage depends on a ±1 SD criterion whose base rate on non-event
  windows is ≈ 69 %; it is reported only relative to that base rate. The classifier drops rows with an
  undefined `gap_trend` (about 60 % of rows; `n_rows` is printed with every AUC).

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_preevent_features.py` | transcripts + metrics + episode/L10 boundaries | `results/preevent_features{,_w30,_w90}.csv` | **yes** |
| `paired_tests.py` | `results/preevent_features*.csv` | `results/paired_tests_w{30,60,90}.csv`, `results/paired_tests_all_windows.csv` | no |
| `classifier_cv.py` | `results/preevent_features.csv` | `results/cv_auc_results.csv`, `results/roc_curves.npz`, `results/single_feature_auc.csv` | no |
| `meso_forecasting.py` | metrics + Study 8 outcomes | `results/meso_halves.csv` (per-meeting, online and global thresholds), `results/meso_budget_sensitivity.csv`, `results/meso_h1_to_h2eventrate.csv`, `results/meso_h1_to_outcomes.csv` | no |
| `null_precursor_rate.py` | `results/preevent_features.csv` | `results/no_precursor_summary.csv`, `results/no_precursor_both.csv` | no |
| `precursor_by_class.py` | Study 9's `events_initiators.csv` + Study 10's precursor data | `results/precursor_by_class.csv`, `results/no_precursor_rate_by_class.csv`, `results/precursor_magnitude_by_class.csv`, `results/precursor_magnitude_pairwise_<feature>.csv` | no |
| `fig_early_warning.py` | `results/preevent_features.csv`, metrics, `results/cv_auc_results.csv`, `results/roc_curves.npz` | `figures/fig_early_warning.png/pdf/svg` | **yes** |

All published outputs are numeric only; `question_density` and similar features are counts/fractions,
never transcript text.

## References
Wiltshire (2026, *Small Group Research*); Scheffer et al. (2009, critical transitions and early-warning
signals) for the abrupt-vs-graded framing; this program's Studies 2, 6, 7, 8, 9 (event definition,
boundary logic, Study 8 outcome data, established statistical conventions). See `references.md`.
