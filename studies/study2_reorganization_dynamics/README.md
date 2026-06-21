# Study 2 — What reorganization is, dynamically

## Rationale and gap
Gorman's framework was developed in the laboratory with *experimental* perturbations that force teams to
adapt. Naturalistic teams provide no such manipulations, so reorganization must be characterised
**endogenously** and tested against null models that themselves oscillate — otherwise any rising-and-
falling signal can be mistaken for structure. This study establishes what reorganization *is* as a
dynamical phenomenon and, importantly, separates the genuine effects from artefacts of measurement or of
trivial oscillation.

## Method
- **Metrics.** Gorman-faithful entropy, %DET, and RMSE (`src/gorman_reimpl.py`; see `METHODS.md`),
  with %DET de-saturated at L_min = 8.
- **Event detection.** Within-meeting control-limit excursions: RMSE peaks (up), %DET valleys (down),
  entropy peaks/valleys (`peaks_gorman.py`).
- **Null models.** AR(1) and bivariate VAR(1) surrogates (`surrogate_validation.py`); a decisive
  speaker-sequence shuffle that preserves the categorical series but destroys its order
  (`speaker_sequence_surrogate.py`); a unimodal-Gaussian null for the "two regimes" claim
  (`clusters_check2.py`).
- **Cycle geometry.** Decomposition of the reorganization cycle into ascending / peak / descending /
  valley phases and the entropy–%DET phase plane (`phase_analysis.py`, `phase_followups.py`).

## Results
**What survives.**
- Reorganization at entropy peaks is roughly **twice** an autoregressive baseline (dispersion of pre-to-
  post entropy change well outside the 95% interval of AR(1) and VAR(1) surrogates).
- A genuine **order ↔ disorder coupling**: pre-to-post changes in entropy and %DET move oppositely and
  exceed a VAR(1) null, though much of the raw coupling is the general entropy–%DET relationship and the
  peak-specific excess is modest.
- **Geometry.** Under a clean, consistent definition of excursions, the **ascending and descending limbs
  are symmetric** (median ≈ 51 vs 52 s; n.s.). A small but consistent hysteresis exists in the entropy–
  %DET plane, but a cross-correlation analysis finds **no robust temporal lead–lag** (lag ≈ 0), so it is
  reported only as a subtle path-dependence.

**What is dropped as artefact (stated transparently).**
- *Two discrete coordination regimes* — the distribution is a continuum; a two-cluster solution does not
  exceed a unimodal-Gaussian null, and the apparent bimodality at L_min = 2 is a **%DET-saturation
  artefact** that disappears once %DET is de-saturated (`clusters_check2.py`).
- *Descent more variable than ascent* — a definitional artefact; clean phases are symmetric.
- *A back-fit event count at "3 SD"* — a reproducible detector requires ≈ 2 SD.
- *"Aggregate cancellation" as evidence* — trivial, since oscillating surrogates also cancel.

## Metric correction disclosed here
An earlier RMSE that predicted the **raw nominal speaker-identifier** series is mis-specified; the
Gorman-faithful RMSE is computed on the **%DET** series (Grimm et al. 2017). The consequence — that the
old "RMSE = argument/disagreement" reading was an artefact — is documented in Study 3.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `peaks_gorman.py` | `data/metrics_gorman_l8/` (+ taxonomy counts) | `results/peaks_summary.csv`, `results/peaks_content_lift.csv` | no |
| `surrogate_validation.py` | metric series | console | no |
| `speaker_sequence_surrogate.py` | metric series | console | no |
| `clusters_check2.py` | metric series | console | no |
| `phase_analysis.py` | `data/metrics_gorman_l8/` (+ taxonomy counts) | `results/phase_asymmetry.csv` | no |
| `phase_followups.py` | metric series (+ transcripts for floor snapshots) | console | partial |

## References
Gorman et al. (2012a,b); Grimm et al. (2017); Kantz & Schreiber (1997); Marwan et al. (2007). See
`references.md`.
