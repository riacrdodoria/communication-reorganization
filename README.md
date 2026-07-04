# Communication reorganization in naturalistic team meetings

**An auditable research repository.**
R. L. Dória & J. C. Gorman.

This repository documents a program of nine interlocking studies on *communication reorganization* in
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

Our central thesis, built across the nine studies, is that in real teams **reorganization is not (only)
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

## 3. The nine studies (in order)

| # | Folder | Question | Headline result |
|---|---|---|---|
| 1 | [`studies/study1_lsh_validation`](studies/study1_lsh_validation) | Is the Last-Speaker-Holds (LSH) representation a valid substrate? | LSH reproduces the standard silence-preserving representation (r ≈ .87–.93). |
| 2 | [`studies/study2_reorganization_dynamics`](studies/study2_reorganization_dynamics) | What *is* reorganization, dynamically? | Endogenous, supra-autoregressive, a continuum (not two regimes); clean entropy–%DET geometry. |
| 3 | [`studies/study3_content_fingerprint`](studies/study3_content_fingerprint) | What does reorganization *mean*? | Coordination, not deliberation — six validated taxonomies converge, corroborated by coding-free measures. |
| 4 | [`studies/study4_floor_dynamics`](studies/study4_floor_dynamics) | What is it in *floor* terms? | Edelsky F1 ↔ F2; the floor equalizes and de-centralizes at reorganization (event-locked). |
| 5 | [`studies/study5_team_development`](studies/study5_team_development) | How does it *develop*? | Over 26 weeks teams consolidate (entropy↓, centrality↑, content→deliberation, range↓), replicated across two teams and three lenses. |
| 6 | [`studies/study6_dialogue_microstructure`](studies/study6_dialogue_microstructure) | At what *unit* does it live? | Topic-episode boundaries *are* reorganization events; meetings follow an open→status→problem→solution→close arc; on the teams' EOS Level 10 agenda the procedural review reorganizes *more* than the deliberative problem-solving (IDS). |
| 7 | [`studies/study7_anatomy_of_reorganization`](studies/study7_anatomy_of_reorganization) | What *is* a single reorganization event? | A redistribution of the floor (F1→F2): ~⅓ topic-transition (deeper) + ~⅔ endogenous handoff/opening (function: clarify / co-construct / decide; κ = .51); trigger sets depth, not existence; each taxonomy predicts both perturbations the same way (both coordination). |
| 8 | [`studies/study8_outcomes`](studies/study8_outcomes) | Does reorganization *matter*? | Tests the adaptive-function proposition (P6) against three EOS L10-embedded outcomes (meeting rating, to-do completion, IDS issue resolution). Honest null: 0/42 predictor×outcome tests (Spearman + mixed model) survive BH-FDR; reported transparently as a null, not hidden. |
| 9 | [`studies/study9_initiators`](studies/study9_initiators) | Who initiates reorganization? | The external facilitator (the same advisor across both teams) initiates in exact proportion to talk-time (permutation test, all n.s.) — no facilitator advantage; the most disproportionate initiator is each team's *quietest* member. A weak, team-dependent drift toward the facilitator over time is reported but not read as evidence for leader-centric consolidation (P5), since the facilitator is external, not either team's own internal leader. |

A reader can begin with Study 1 and proceed in order; each study folder has a self-contained `README.md`
with rationale, methods, the exact analysis scripts, the result tables they produce, and references.

## 4. Repository layout

```
README.md                 this overview
METHODS.md                shared methods and conventions used throughout
DATA.md                   data description, anonymisation, and availability
references.md             full bibliography
requirements.txt          Python dependencies
src/                      shared module (Gorman-faithful metric construction)
studies/study1..9/        one folder per study: README + analysis scripts
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

## 7. Reproducibility and annotation

Metrics follow the Gorman/Grimm specification (see `METHODS.md`). Interaction-taxonomy annotation was
performed with large-language-model annotators applied to the published codebook definitions, following
the validation practice recommended by Pangakis, Wolken & Fasching (2023): automated annotation is used
at scale and is to be validated against a human-coded subset (κ). All inferential tests treat the
**meeting** as the unit of inference and use within-meeting null models with Benjamini–Hochberg FDR
control. See `METHODS.md` for details. Full references in [`references.md`](references.md).
