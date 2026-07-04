# Study 10 — Anticipating reorganization (early-warning signatures)

## Rationale and gap
Wiltshire (2026, *Small Group Research*) closes by calling the field to move beyond post hoc
description toward anticipating coordination breakdowns and supporting adaptive teamwork in real
time. This study answers that call inside our corpus, as a **feasibility probe** — not a production
classifier. Two questions: (1) **micro** — do the 30–90 s preceding a reorganization event carry a
detectable signature relative to matched non-event baselines? (2) **meso** — do first-half-of-meeting
dynamics predict the meeting's own second half and its Study-8 outcome rating?

## Method
909 reorganization events (34 meetings; same detector as Studies 2/6/7/9: RMSE > mean+2.33 SD, 8 s gap
clustering). Six features over the **[−60, 0) s window before onset** (30/90 s reruns for
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
- **72.5% of events show no detectable `entropy_slope` precursor** and **51.7% show none on
  `switch_rate`** by a conservative, meeting-internal (±1 SD) criterion; **35.1% show none on either**.
  Read honestly against the critical-transitions literature: a majority of these reorganizations are not
  reliably "ramped into" by the measured features — some may be closer to abrupt, discontinuous shifts.
- **A genuine meso-level finding, independent of the early-warning question**: a meeting's first-half
  reorganization rate *negatively* predicts its own second-half rate (Spearman ρ = −0.64, q < .001),
  replicated in both teams independently — within-meeting self-regulation, not momentum. First-half
  dynamics do **not** forecast Study 8's meeting-rating outcomes (0/9 tests survive BH-FDR), consistent
  with — and not double-publishing — Study 8's own null.

Full statistics, the complete leakage audit, and honest interpretation: `RESULTS.md`.

## Honest scope
- 2 teams, 34 meetings — replication, not generalization, as throughout this program.
- A single fixed regularization default is used for the classifier (no tuning), by design, given the
  guardrail against AUC-chasing at this sample size.
- The event/RMSE detection threshold is computed per meeting from that meeting's own full RMSE series
  (established convention throughout this program) — this is appropriate for retrospective analysis but
  is not purely causal/online, which is precisely why this study is framed as a feasibility probe and
  not a specification for a live monitoring system.
- The "no detectable precursor" percentage depends on a disclosed, reasonable but not unique threshold
  (±1 SD); the AUC results (T2) corroborate the same qualitative picture using a model-based criterion
  that does not depend on this specific choice.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_preevent_features.py` | transcripts + metrics + episode/L10 boundaries | `results/preevent_features{,_w30,_w90}.csv` | **yes** |
| `paired_tests.py` | `results/preevent_features*.csv` | `results/paired_tests_w{30,60,90}.csv`, `results/paired_tests_all_windows.csv` | no |
| `classifier_cv.py` | `results/preevent_features.csv` | `results/cv_auc_results.csv`, `results/roc_curves.npz`, `results/single_feature_auc.csv` | no |
| `meso_forecasting.py` | metrics + Study 8 outcomes | `results/meso_halves.csv`, `results/meso_h1_to_h2eventrate.csv`, `results/meso_h1_to_outcomes.csv` | no |
| `null_precursor_rate.py` | `results/preevent_features.csv` | `results/no_precursor_summary.csv`, `results/no_precursor_both.csv` | no |
| `fig_early_warning.py` | `results/preevent_features.csv`, metrics, `results/cv_auc_results.csv`, `results/roc_curves.npz` | `figures/fig_early_warning.png/pdf/svg` | **yes** |

All published outputs are numeric only; `question_density` and similar features are counts/fractions,
never transcript text.

## References
Wiltshire (2026, *Small Group Research*); Scheffer et al. (2009, critical transitions and early-warning
signals) for the abrupt-vs-graded framing; this program's Studies 2, 6, 7, 8, 9 (event definition,
boundary logic, Study 8 outcome data, established statistical conventions). See `references.md`.
