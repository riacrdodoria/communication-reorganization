# Methods and conventions (shared across studies)

This file documents the constructs, metric definitions, and statistical conventions used throughout the
twelve studies, so that they are stated once and referenced everywhere.

## 1. Corpus

Thirty-four naturalistic advisory ("Pulse") meetings of two early-stage venture teams (anonymised as
*Team A* and *Team B*), recorded approximately weekly from 14 Oct 2024 to 14 Apr 2025 (~26 weeks; 17
meetings per team). Each meeting pairs the team with the same advisor. One additional recording was
excluded because its automatic transcription was generated with the wrong-language model and was
unusable; one further recording was a short partial and was excluded. Transcripts give, per utterance,
an onset time (whole-second resolution), an anonymous speaker identifier, and the (withheld) text.

**Transcription-tool line (corrected 2026-09-05).** From 17 March 2025 the transcription tool inserted one
automatic announcement line at the start of each recording (one utterance, 11 words, within the first six
minutes). In the ten affected meetings (the last five weeks of both teams) that line had been carried as an
additional anonymous speaker, inflating the speaker count used to normalise entropy (%MaxEnt = H / n_speakers)
by one and deflating entropy by 20–25 % in exactly those meetings. The line is removed from the canonical
transcripts before any metric is computed (`src/remove_bot_rows.py`); the metric series in
`data/metrics_gorman_l8/` and every downstream table are computed on the cleaned corpus. Episode boundaries
stored as utterance indices were shifted accordingly (`src/patch_episode_indices_nobot.py`); no boundary
coincided with the removed line.

**Speaker identity.** The anonymous `speaker_id` is assigned *per meeting* by order of first appearance and
is therefore not a persistent identity across meetings. Any analysis that aggregates over a person across
meetings (Study 9, Study 11) uses the verified per-meeting role map `results/speaker_roles_verified.csv`
(`src/roles.py`): FACILITATOR (the same external advisor in every meeting of both teams) and A1–A3 / B1–B3
(team members; one Team B member joined nine meetings through a shared team account rather than a
personal one and is mapped to the same role, B2). The map was built by aligning each
anonymised transcript with the researcher's retained, name-labelled source transcript; the source files and
the name→role key are not distributed.

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

**Canonical event definition (Studies 7, 9, 10, 12).** Event-seconds are those with RMSE > mean + 2.33 · SD
of the meeting's own RMSE series (population SD, NaN-free seconds). Consecutive event-seconds separated by
≤ 8 s form one event (`src/reorg_events.py`). The RMSE at second *i* is the forecast error over the next 20 s,
so an event timestamp marks the *start* of the mispredicted stretch. Study 2's surrogate tests use a
separate, entropy-based detector (local maxima above mean + 2 · SD, ≥ 60 s apart, ±90 s pre/post windows);
its parameters are stated in that study.

**Trigger classification.** An event is a TRANSITION if its centre lies within ±30 s of a topic-episode or
EOS Level 10 stage boundary; otherwise INTERIOR_HANDOFF if the dominant floor-holder (by turn count) differs
in the 30 s before vs after the event centre, else INTERIOR_OTHER. One implementation is shared by all
studies (`src/reorg_events.py`). The handoff/other split is sensitive to the rule (275/170 canonical; 195–275
handoffs across five reasonable variants, 57–78 % agreement, `results/reorg_class_sensitivity.csv`); the
TRANSITION class is not.

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
- **Permutation p-values** are reported as (b + 1)/(N + 1) (Phipson & Smyth 2010) and never as 0; with
  N = 1,000 the two-sided floor is p < .002, with N = 2,000 p < .0005, with N = 10,000 p < .0001.
- **Resampling seeds** are fixed constants (bootstrap seeds derived from a CRC of the statistic name, not
  from Python's per-process `hash()`), so every interval in `results/` regenerates exactly.
- **Sarle's bimodality coefficient** is (g1² + 1) / (g2 + 3(n−1)²/((n−2)(n−3))) with g2 the *excess*
  kurtosis (a Gaussian gives 1/3; > 0.555 suggests bimodality).
- **Longitudinal trends** (Kendall τ over 17 weeks per team) are computed on the bot-cleaned metrics;
  because the ten late meetings were the only ones affected by the transcription-tool line, any trend in
  absolute entropy computed on the uncleaned corpus is confounded with time and is not reported.

## 7. Turn-length confounding (important)

Lexical-rate and text-dynamics measures (function-word proportions, LIWC categories, but also TF-IDF
recurrence and turn-to-turn coherence, which are computed over utterances) can become proxies for turn
length, and utterance segmentation is the very turn structure the turn-taking metrics are built from.
Wherever such a measure is related to reorganization, the association is **also computed within meeting
after partialling out turn length** (primary control; the Stouffer combination of the residualised
within-meeting associations under the circular-shift null), and, as a sensitivity analysis, after
partialling out turn length and turns-per-window jointly. Only effects surviving the primary control are
read as content evidence (Study 3, `results/triangulation_Z.csv`). Note that turns-per-window is itself
strongly coupled to %DET (within-meeting r ≈ −.8), so the joint control can over-adjust and is reported
only as a bound.

## 8. Corrections log

- **2026-09-05.** (i) Transcription-tool line removed from ten meetings (§1); all metric series, tables and
  figures regenerated. Longitudinal entropy declines previously reported in Studies 5 and 7 do not survive
  (Study 5 τ = −.09 / −.16, n.s.; Study 7 baseline τ = −.16, n.s.; 0/10 developmental trends pass FDR).
  (ii) Facilitator identified per meeting from the verified role map (Study 9; earlier a single constant
  id was wrong in 24/34 meetings), and all cross-meeting person-level statistics rebuilt on roles.
  (iii) Study 2 surrogate tests rerun on the L_min = 8 %MaxEnt metrics (earlier numbers came from a
  retired 1 Hz raw-bits implementation); bimodality coefficient corrected (0.18 → 0.41; conclusion
  unchanged). (iv) Study 3 coding-free measures re-tested under the turn-length control (§7): semantic
  recurrence and coherence do not survive; novelty does. (v) Study 10 within-meeting "budget" shown to be
  an artefact of the per-meeting event threshold (online threshold ρ = +.03); "no precursor" rates now
  reported against the criterion's base rate. (vi) One shared event-classification implementation (§4);
  Study 7 trigger→magnitude contrast re-tested at the meeting level. (vii) Turn-transition network
  measures corrected (`src/floor_measures.py`): Freeman centralization normalised, principal eigenvector by
  eigendecomposition, degenerate in/out asymmetry replaced by dyadic transition asymmetry.
