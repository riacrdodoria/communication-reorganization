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
- **Null models.** AR(1) and bivariate VAR(1) surrogates (`surrogate_validation.py`, run on the L_min = 8
  %MaxEnt metrics; the `--legacy` flag reproduces the earlier run on a retired 1 Hz raw-bits
  implementation, which is where the previously reported 0.405 vs 0.190 came from); a team-state
  run-order shuffle that preserves every state's total time and the run-length distribution but destroys
  temporal arrangement, with entropy and %DET recomputed exactly as in `src/gorman_reimpl.py`
  (`speaker_sequence_surrogate_l8.py`; `speaker_sequence_surrogate.py` is the legacy version); a
  unimodal-Gaussian null for the "two regimes" claim (`clusters_check2.py`) and Sarle's bimodality
  coefficient (`METHODS.md` §6).
- **Cycle geometry.** Decomposition of the reorganization cycle into ascending / peak / descending /
  valley phases and the entropy–%DET phase plane (`phase_analysis.py`, `phase_followups.py`).

## Results
**What survives.**
- Reorganization at entropy peaks is **supra-autoregressive**: the SD of the pre-to-post entropy change
  at peaks is 14.8 %MaxEnt against 6.5 [5.6, 7.4] under AR(1) and 6.5 [5.4, 7.8] under VAR(1) surrogates
  (200 runs each, 49 events; `results/surrogate_validation_results.csv`) — 2.3× the null, outside its 95 %
  interval. (The earlier 0.405 vs 0.190 was the same ratio in raw bits from the retired implementation.)
- The **entropy ↔ %DET coupling is a property of the two metrics, not of temporal organisation.** The
  pre-to-post changes are strongly anticorrelated (r = −.78) and exceed the VAR(1) null (−.33), but the
  run-order shuffle — which keeps each team state's total time and destroys *when* it occurs — reproduces
  it: null mean r = −.71, 95 % [−.88, −.48] (200 shuffles, `results/seq_surrogate_l8_null.csv`). An earlier
  version listed the coupling under "what survives" on the strength of the VAR(1) test alone; the
  decisive shuffle test had already shown it to be reproducible and it is now reported as such.
- **Geometry.** Under a clean, consistent definition of excursions, the **ascending and descending limbs
  are symmetric** (median ≈ 51 vs 52 s; n.s.). A small but consistent hysteresis exists in the entropy–
  %DET plane, but a cross-correlation analysis finds **no robust temporal lead–lag** (lag ≈ 0), so it is
  reported only as a subtle path-dependence.

**What is dropped as artefact (stated transparently).**
- *Two discrete coordination regimes* — the distribution is a continuum; a two-cluster solution does not
  exceed a unimodal-Gaussian null, and the apparent bimodality at L_min = 2 is a **%DET-saturation
  artefact** that disappears once %DET is de-saturated (`clusters_check2.py`). Sarle's bimodality
  coefficient on pooled entropy is **0.41** (< 0.555; Team A 0.39, Team B 0.44). An earlier figure of 0.18
  came from a formula that used Pearson rather than excess kurtosis (`METHODS.md` §8); the conclusion is
  unchanged.
- *Descent more variable than ascent* — a definitional artefact; clean phases are symmetric.
- *A back-fit event count at "3 SD"* — a reproducible detector requires ≈ 2 SD.
- *"Aggregate cancellation" as evidence* — trivial, since oscillating surrogates also cancel.
- *Entropy–%DET coupling as temporal coordination* — reproducible by shuffling the order of team-state
  runs (above).

## Metric correction disclosed here
An earlier RMSE that predicted the **raw nominal speaker-identifier** series is mis-specified; the
Gorman-faithful RMSE is computed on the **%DET** series (Grimm et al. 2017). The consequence — that the
old "RMSE = argument/disagreement" reading was an artefact — is documented in Study 3.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `peaks_gorman.py` | `data/metrics_gorman_l8/` (+ taxonomy counts) | `results/peaks_summary.csv`, `results/peaks_content_lift.csv` | no |
| `surrogate_validation.py` | `data/metrics_gorman_l8/` (`--legacy`: retired 1 Hz metrics, not shipped) | `results/surrogate_validation_results.csv`, console | no |
| `speaker_sequence_surrogate_l8.py` | transcripts (team-state series) + `data/metrics_gorman_l8/` | `results/seq_surrogate_l8_null.csv`, console | **yes** |
| `speaker_sequence_surrogate.py` | retired 1 Hz metrics (not shipped; legacy) | console | no |
| `clusters_check2.py` | metric series (partly legacy inputs) | console | no |
| `phase_analysis.py` | `data/metrics_gorman_l8/` (+ taxonomy counts) | `results/phase_asymmetry.csv` | no |
| `phase_followups.py` | metric series (+ transcripts for floor snapshots) | console | partial |

## References
Gorman et al. (2012a,b); Grimm et al. (2017); Kantz & Schreiber (1997); Marwan et al. (2007). See
`references.md`.
