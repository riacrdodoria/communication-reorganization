# Methods and conventions (shared across studies)

This file documents the constructs, metric definitions, and statistical conventions used throughout the
nine studies, so that they are stated once and referenced everywhere.

## 1. Corpus

Thirty-four naturalistic advisory ("Pulse") meetings of two early-stage venture teams (anonymised as
*Team A* and *Team B*), recorded approximately weekly from 14 Oct 2024 to 14 Apr 2025 (~26 weeks; 17
meetings per team). Each meeting pairs the team with the same advisor. One additional recording was
excluded because its automatic transcription was generated with the wrong-language model and was
unusable; one further recording was a short partial and was excluded. Transcripts give, per utterance,
an onset time (whole-second resolution), an anonymous speaker identifier, and the (withheld) text.

## 2. Turn-taking representation

- **Last-Speaker-Holds (LSH).** Each second inherits the most recent speaker to have taken the floor,
  preserving floor-holding continuity. Study 1 validates LSH against the standard active-speaker
  representation (in which silence and floor gaps are separate states).
- **Multi-speaker team states.** For the dynamical metrics we form binary multi-speaker states (overlaps
  allowed), with each utterance occupying the grid from its onset to onset + 0.5 · (number of words),
  i.e. a 2-words-per-second interpolation, sampled at 2 Hz (`src/gorman_reimpl.py`).

## 3. Reorganization metrics (Gorman/Grimm specification)

Computed on a 60 s sliding window with 1 s step (`src/gorman_reimpl.py`):

- **Entropy.** Shannon entropy of the team-state distribution, normalised by log2(2^n_speakers) and
  expressed as a percentage of maximum entropy (%MaxEnt).
- **%DET (percent determinism).** From a discrete recurrence plot of the team-state series: the
  proportion of recurrent points that lie on diagonal lines (minimum line length L_min). Following the
  recurrence-quantification literature.
- **RMSE.** Nonlinear prediction error by the *method of analogues* (Kantz & Schreiber 1997) computed
  **on the %DET series** (not on the raw speaker series): for each point, neighbours within ε = 3 %DET
  are found, their forward trajectories (horizon Δn = 20 s) averaged, and the RMSE between the predicted
  and actual trajectory recorded. This matches Grimm et al. (2017); a prior implementation that predicted
  the raw nominal speaker-identifier series is mis-specified and is not used (see Study 3).

### %DET de-saturation (L_min)
Because onsets are recorded at 1 s resolution, the team-state series is "blocky" and %DET saturates near
its ceiling at L_min = 2. Widening the window or normalising does not remedy this; increasing the minimum
diagonal length to **L_min = 8** restores %DET into the range reported by Grimm et al. (median ≈ 87,
SD ≈ 18) and is used as the primary setting, reported as a sensitivity choice. The metric series provided
in `data/metrics_gorman_l8/` use L_min = 8.

## 4. Event detection

Reorganization events are detected within each meeting as excursions beyond an upper/lower control limit,
UCL/LCL = mean ± t · SD (t = 1.65 for p < .05, t = 2.33 for p < .01). RMSE shows upward peaks; %DET shows
downward valleys at the same moments; entropy shows both.

## 5. Interaction-taxonomy annotation

Six previously validated coding schemes are used verbatim (definitions in
`studies/study3_content_fingerprint/codebook_defs.md`): CACS conversational argument; Gunawardena IAM
knowledge-construction phases; Mercer talk types; Bales Interaction Process Analysis; act4teams-SHORT;
and ISO 24617-2 dialogue acts. Annotation is performed by large-language-model annotators applied to the
codebook definitions, following the validation practice of Pangakis et al. (2023): automated annotation
at scale, to be validated against a human-coded subset (Cohen's κ). Counts are produced per 90 s window
(`data/codebooks/`, `data/codebooks2/`) and, in Study 6, per topic episode (`data/codebooks_episode/`).

## 6. Statistical conventions

- **Unit of inference = the meeting.** Within-meeting associations are computed first, then combined
  across meetings (Stouffer Z or Fisher-z), so that windows/episodes within a meeting are not treated as
  independent.
- **Within-meeting null models.** Continuous cross-references use a within-meeting circular-shift null
  (rolling one series relative to the other); dynamic claims in Study 2 are additionally benchmarked
  against AR(1) and bivariate VAR(1) surrogates and a speaker-sequence shuffle.
- **Multiple comparisons.** Benjamini–Hochberg FDR control within each family of tests.
- **Two teams.** For the longitudinal analyses (Study 5), n = 2 teams precludes between-team statistical
  generalisation; the criterion is **direction-consistency across the two teams**, treated as replication
  rather than statistical power.

## 7. Turn-length confounding (important)

Lexical-rate measures (e.g. proportions of function words or LIWC categories) can become proxies for turn
length, which is itself tied to the turn-taking metrics. Wherever a lexical-rate measure is related to
reorganization, the association is also computed **controlling for turn length** (partial correlation);
only effects surviving that control are retained (see Study 3).
