# Communication reorganization in naturalistic team meetings

**An auditable research repository.**
R. L. Dória & J. C. Gorman.

This repository documents a program of twelve interlocking studies on *communication reorganization* in
real teams, analysed from 34 naturalistic advisory meetings of two early-stage venture teams recorded
weekly over ~6 months. It is organised for full transparency: every analysis script, every (numeric)
intermediate and result table, and every figure is included so that an independent reader can audit
each study end to end. The confidential meeting transcripts themselves are withheld (see
[Data availability](#data-availability)).

---

## 1. The phenomenon and the central thesis

When a team talks, the *structure* of who holds the conversational floor continually restructures — it
tightens onto a single speaker and opens up among several. Following Gorman and colleagues, we quantify
this with dynamical-systems measures of the team's turn-taking series: the Shannon **entropy** of the
multi-speaker state, the **percent determinism (%DET)** of its recurrence plot, and a nonlinear-prediction
**RMSE** computed on the %DET series. Peaks and valleys in these series mark moments of *reorganization*.

Our central thesis, built across the twelve studies, is that in real teams **reorganization is not (only)
externally-forced perturbation–recovery — it is an endogenous, bidirectional process organised along a
single axis: deliberation ↔ coordination**, which in conversation-analytic terms is Edelsky's
*singly-developed* (F1) ↔ *collaborative* (F2) floor. This axis recurs, convergently, across **what** is
said (validated interaction taxonomies), **how** it is said (coding-free text-dynamics measures), **who**
holds the floor (participation and network centrality), **when** it shifts (topic-episode transitions),
and **how** it changes as a team matures (developmental consolidation).

## 2. Gaps this work addresses

1. **Naturalistic and longitudinal scope.** The dynamical-systems account of team communication is almost
   entirely laboratory-based, short-term, and built on experimental perturbations. In-the-wild,
   multi-month, real-team reorganization is rarely studied.
2. **The meaning of the metrics.** Gorman-style metrics are purely mechanical (turn-taking only); content
   is typically used only post-hoc to narrate peaks. What reorganization *corresponds to* substantively
   has not been mapped systematically.
3. **An unmade cross.** The conversation-floor / participation / centrality literature and the
   entropy / recurrence dynamical-systems literature have not been related to each other.
4. **Development over time.** How communication reorganization unfolds across a team's life is rarely
   examined with fine-grained, repeated measures.
5. **Methodological rigour.** Dynamic claims in this area are easy to over-state; this work benchmarks
   every dynamic claim against null models and validates automated annotation against published practice.

## 3. The twelve studies (in order)

| # | Folder | Question | Headline result |
|---|---|---|---|
| 1 | [`studies/study1_lsh_validation`](studies/study1_lsh_validation) | Is the Last-Speaker-Holds (LSH) representation a valid substrate? | LSH reproduces the standard silence-preserving representation: r ≈ .87–.93 on Gorman's published validation corpora (earlier 1 Hz implementation), median r = .94 on the present 34 meetings (Gorman-faithful metrics). |
| 2 | [`studies/study2_reorganization_dynamics`](studies/study2_reorganization_dynamics) | What *is* reorganization, dynamically? | Endogenous and supra-autoregressive (entropy excursions 2.3× the AR(1)/VAR(1) null, L_min = 8 metrics); a continuum, not two regimes (Sarle BC = 0.41 < 0.555); the entropy–%DET coupling is reproduced by shuffling the order of team-state runs, i.e. it is a property of the two metrics, not of temporal organisation. |
| 3 | [`studies/study3_content_fingerprint`](studies/study3_content_fingerprint) | What does reorganization *mean*? | Coordination, not deliberation — six validated taxonomies converge (28/40 categories at RMSE peaks, 27/40 at %DET valleys; unchanged after the corpus correction). Among coding-free measures, only novelty/topic-shift survives the turn-length control; semantic recurrence and coherence were turn-length artefacts. |
| 4 | [`studies/study4_floor_dynamics`](studies/study4_floor_dynamics) | What is it in *floor* terms? | Edelsky F1 ↔ F2; the floor equalizes and de-centralizes at reorganization (event-locked; nine measures, corrected network statistics). |
| 5 | [`studies/study5_team_development`](studies/study5_team_development) | How does it *develop*? | After removing a transcription-tool line that had inflated the speaker count in the ten latest meetings, the previously reported entropy decline vanishes (τ = −.09 / −.16, n.s.). What remains: network centralization rises in Team B (τ = +.43) and in direction in Team A (+.32); content trends 0/82 after FDR. Development is *not* a consolidation of the resting operating point. |
| 6 | [`studies/study6_dialogue_microstructure`](studies/study6_dialogue_microstructure) | At what *unit* does it live? | Topic-episode boundaries *are* reorganization events; meetings follow an open→status→problem→solution→close arc; on the teams' EOS Level 10 agenda the procedural review reorganizes *more* than the deliberative problem-solving (IDS). |
| 7 | [`studies/study7_anatomy_of_reorganization`](studies/study7_anatomy_of_reorganization) | What *is* a single reorganization event? | A redistribution of the floor (F1→F2): ~⅓ topic-transition + ~⅔ endogenous handoff/opening (function: clarify / co-construct / decide; κ = .51). Trigger classes are graded, TRANSITION > HANDOFF > OTHER, on all three metrics at the meeting level (paired Wilcoxon p = .04 / .0002 / .004), and 37/40 taxonomy categories move the same way at both. Developmentally, neither the resting baseline nor the event excursion drifts once the corpus is corrected (0/10 trends survive FDR). |
| 8 | [`studies/study8_outcomes`](studies/study8_outcomes) | Does reorganization *matter*? | Tests the adaptive-function proposition (P6) against three EOS L10-embedded outcomes (meeting rating, to-do completion, IDS issue resolution). Honest null: 0/42 predictor×outcome tests (Spearman + mixed model) survive BH-FDR; reported transparently as a null, not hidden. |
| 9 | [`studies/study9_initiators`](studies/study9_initiators) | Who initiates reorganization? | With the facilitator identified per meeting (verified role map) and members tracked as persons rather than per-meeting labels: the external facilitator initiates *fewer* floor-taking and topic-opening events than talk-time predicts (permutation p < .002, both definitions; lift 0.86 / 0.75) but *more* question-initiated events (p = .008); the least-talkative member over-initiates in both teams (lift 1.38 / 1.75); initiator ranks are stable across halves in Team A (ρ = .80–1.00) and, in Team B, on the floor definition (1.00) but not on the primary one (.20), where the facilitator's share rises in the second half. |
| 10 | [`studies/study10_early_warning`](studies/study10_early_warning) | Can reorganization be anticipated? | A feasibility probe (not a classifier): a real, mechanism-independent precursor exists (rising speaker-switching, shortening turns, fewer questions before events) but is only modestly discriminable event-by-event (AUC ≈ 0.66). The earlier "within-meeting budget" (first-half rate negatively predicting second half) was an artefact of the per-meeting event threshold: with an online threshold ρ = +.03 (n.s.), and a circular-shift null reproduces the negative value. "No detectable precursor" (72 %) equals the criterion's base rate on baseline windows (69 %). |
| 11 | [`studies/study11_replication`](studies/study11_replication) | Does everything above replicate across the two teams? | Formalizes the corpus as an intensive longitudinal replication design. 26/27 headline statistics agree in direction; the decisive test — four entire multi-category profiles (taxonomy fingerprint, floor measures, review-vs-IDS contrast, border-vs-interior contrast) — correlate between teams at Spearman r = 0.84–0.98 (permutation p < .0001, 0/10,000). Of five longitudinal trends, only network centralization replicates (partially); the entropy trends are null in both teams after the corpus correction. Of the person-level statistics, the least-talkative-member lift replicates; initiator-rank stability and the facilitator's longitudinal share differ by team, both reflecting the facilitator's rising share in Team B's second half. |
| 12 | [`studies/study12_socioemotional`](studies/study12_socioemotional) | Does reorganization have a socioemotional face? | Yes, and it is one-sided: agreement, positive affect, and solidarity rise sharply at reorganization events (BH-FDR q<.001, within an 8-category confirmatory family); no negative category survives FDR. The positive signal is a sharp spike coincident with the event itself (circular-shift null p<.02), not a before-the-fact lubricant or after-the-fact repair. Negative affect instead concentrates in the deliberative IDS stage, not at reorganization events. |

A reader can begin with Study 1 and proceed in order; each study folder has a self-contained `README.md`
with rationale, methods, the exact analysis scripts, the result tables they produce, and references.

### Corrections (2026-09-05)

A full code audit of the twelve studies found two corpus-level defects and several analysis defects, all
now corrected and logged in `METHODS.md` §8. In brief: (1) a transcription-tool announcement line had been
counted as an extra speaker in the ten latest meetings, deflating entropy there by 20–25 % and manufacturing
the developmental entropy decline reported earlier in Studies 5 and 7 (now null); (2) the facilitator had
been identified by a per-meeting label that was wrong in 24 of 34 meetings (Study 9 and the two affected
Study 11 rows rebuilt on a verified role map); (3) the Study 2 surrogate tests, the bimodality coefficient,
the Study 3 coding-free corroboration, the Study 10 "budget", and the Study 4 network measures were
re-derived. Everything that survives is listed in the table above; what did not survive is stated in the
study READMEs rather than removed.

## 4. Repository layout

```
README.md                 this overview
METHODS.md                shared methods and conventions used throughout
DATA.md                   data description, anonymisation, and availability
references.md             full bibliography
requirements.txt          Python dependencies
src/                      shared module (Gorman-faithful metric construction)
studies/study1..12/       one folder per study: README + analysis scripts
data/                     numeric inputs only (metrics, taxonomy counts, episode boundaries)
results/                  numeric result tables produced by the analyses
figures/                  all figures
```

## 5. How to audit

- **Read** each study's `README.md` for the rationale, method, and how each number was produced.
- **Inspect the code** in `studies/` and `src/` — every analysis is a short, self-contained script.
- **Check the numbers** against the provided tables in `results/` and the per-meeting data in `data/`.
- Scripts that operate only on the numeric data in `data/` are runnable as provided; scripts that read
  the raw transcript text require the withheld transcripts (clearly noted in each study README).

## 6. Data availability

The meeting transcripts contain confidential participant speech and are **not** included. To preserve
auditability without exposing them, the repository ships the full **numeric** derivations: per-second
metric series, taxonomy counts per window and per episode, episode boundaries (as utterance indices and
timestamps), and all result tables. Speakers are referred to only by anonymous integer identifiers. The
BP-LIWC2015 dictionary used in Study 3 is licensed and is **not** redistributed (see
[`studies/study3_content_fingerprint/README.md`](studies/study3_content_fingerprint/README.md)).

## 7. Future work

The corrected corpus, the verified per-meeting role map and the quote-anchored issue annotations make four
follow-up questions answerable without new data; they are deliberately left out of the present paper so
that it stays focused on what reorganization is and when it occurs.

1. **Adaptive function at the issue level.** Every issue raised in the IDS stage has a timestamp and a
   resolved / not-resolved status. Whether reorganization occurs when an issue is raised, and whether
   resolved and unresolved issues differ in their reorganization profile, tests the adaptive-function
   proposition on hundreds of units instead of 34 meetings.
2. **The facilitator's question as a cue.** The facilitator asks the opening question more often than
   talk-time predicts while members take the floor. A lagged sequence test (facilitator question at *t*,
   member-initiated event within the following 30 s, against a circular-shift null) would turn this
   division of labour into an observable mechanism.
3. **Member absence as a naturalistic perturbation.** In six meetings one member is absent, so the
   team meets as a dyad with the facilitator. These are the closest in-the-wild analogues to the
   severed-channel perturbations of the laboratory paradigm.
4. **What the floor-openers say.** With events labelled by initiator role, the taxonomy lifts can be
   split by who opened the floor, asking whether bottom-up openings carry different content from
   facilitator-led ones.

## 8. Reproducibility and annotation

Metrics follow the Gorman/Grimm specification (see `METHODS.md`). Interaction-taxonomy annotation was
performed with large-language-model annotators applied to the published codebook definitions, following
the validation practice recommended by Pangakis, Wolken & Fasching (2023): automated annotation is used
at scale and is to be validated against a human-coded subset (κ). All inferential tests treat the
**meeting** as the unit of inference and use within-meeting null models with Benjamini–Hochberg FDR
control. See `METHODS.md` for details. Full references in [`references.md`](references.md).
