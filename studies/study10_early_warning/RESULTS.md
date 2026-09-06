# Study 10 — Anticipating reorganization (early-warning signatures)

> **Correction notice (2026-09-05).** Two conclusions in this file are withdrawn: the within-meeting
> "budget" (first-half rate negatively predicting second-half rate, ρ = −.64) is an artefact of the
> per-meeting event threshold (online threshold ρ = +.03; circular-shift null reproduces −.64;
> `results/meso_budget_sensitivity.csv`), and the "no detectable precursor" percentages are at the base rate
> of the ±1 SD criterion on non-event windows (69 %; `results/no_precursor_summary.csv`). The corpus was also
> cleaned (913 events) and the trigger classes now come from the shared rule (`METHODS.md` §4). See
> `README.md` for the current statement; where this file and `results/` disagree, `results/` is current.

## Framing
Wiltshire (2026, *SGR*) closes by calling the field to move beyond post hoc description toward
anticipating coordination breakdowns and supporting adaptive teamwork in real time. This is a
**feasibility probe** for that call inside our corpus — not a production classifier. We report
discriminability, honestly bounded, not a deployment claim.

## Objective
1. **Micro**: do the 30–90 s preceding a reorganization event carry a detectable signature relative to
   matched non-event baselines?
2. **Meso**: do first-half-of-meeting dynamics predict the meeting's own second half (event rate) and
   its outcome rating (Study 8)?

## Method
909 reorganization events (34 meetings; same detector as Studies 2/6/7/9/etc.: RMSE > mean+2.33 SD per
meeting, contiguous seconds clustered with an 8 s gap rule). For each event, 6 features are computed
over the **[−60, 0) s window immediately before onset** (primary; 30/90 s reruns for sensitivity):
`entropy_slope`, `det_slope` (OLS slopes of entropy_g/det_g across the window), `switch_rate`
(speaker switches/min), `turnlen_trend` (slope of per-utterance word count), `question_density` (share
of utterances containing "?"), `gap_trend` (slope of inter-utterance silence gaps). Each event is
matched to **3 seeded baseline windows** in the same meeting: same EOS L10 stage where possible, and
≥90 s from every event onset in that meeting (909 events × 3 → 2,727 baselines; 3,636 total rows).

## T1 — Pre-event vs matched-baseline (paired, per-meeting, W=60 s primary)
| feature | event mean | baseline mean | rank-biserial | q (BH-FDR) |
|---|---:|---:|---:|---|
| entropy_slope | +0.142 | −0.010 | **+0.94** | <.001 *** |
| det_slope | −0.186 | +0.014 | **−1.00** | <.001 *** |
| switch_rate (per min) | 5.87 | 3.79 | **+1.00** | <.001 *** |
| turnlen_trend | +1.30 | +4.66 | **−0.91** | <.001 *** |
| question_density | 0.367 | 0.480 | **−0.97** | <.001 *** |
| gap_trend | +0.057 | +0.115 | −0.25 | .215 (n.s.) |

**Five of six features show near-maximal, meeting-consistent effects** (rank-biserial ≈ .9–1.0 —
i.e. the direction holds in nearly every one of the 34 meetings). **Important caveat on what this does
and does not license**: `entropy_slope`/`det_slope` are *expected* to show a precursor pattern **by
construction** — a 60 s window ending just before an entropy peak/%DET valley will mechanically tend to
show a local rising/falling trend simply because it approaches a local extremum. Their huge effect
sizes are therefore **not surprising** and should not be read as an independent early-warning
discovery. The genuinely informative result is that the three **behavioral/text features with no
mechanical tie to how entropy_g/det_g/rmse_g are computed** — `switch_rate`, `turnlen_trend`,
`question_density` — *also* show large, highly significant, meeting-consistent effects: **more speaker
switching, shorter/choppier turns, and *fewer* questions (not more) precede reorganization.**
`gap_trend` (silence-gap trend) is the one null: it does not discriminate at any timescale (see T4).

## T2 — Simple discriminability check (leave-one-meeting-out CV)
Two models, reported side by side (the split is the honest core of this study):

| model | features | pooled AUC | 95% CI (meeting-bootstrap) |
|---|---|---:|---|
| **FULL** | all 6 (incl. entropy/%DET slope) | 0.684 | [0.650, 0.716] |
| **BEHAVIORAL** | switch_rate, turnlen_trend, question_density, gap_trend only | 0.662 | [0.624, 0.701] |

Single-feature AUCs (behavioral only): `switch_rate` 0.696 [0.662, 0.728], `question_density` 0.635
[0.599, 0.667], `turnlen_trend` 0.633 [0.593, 0.672], `gap_trend` 0.480 [0.455, 0.512] (chance).

**Reading.** Restricting to features with *no* mechanical link to the reorganization metric itself, an
individual 60 s pre-event window is discriminable from a matched baseline at **AUC ≈ 0.66** — real,
well above chance (CI excludes .5), but modest. This is the central honest tension of the study: **the
same signal that is nearly deterministic at the meeting level (T1, rank-biserial ≈ .9) is only modestly
discriminable at the single-event level (T2, AUC ≈ .66–.68)**. Both are true simultaneously because the
meeting-level test asks "does this meeting's *average* pre-event window differ from baseline" (answer:
almost always, yes) while the event-level test asks "can I tell *this specific* 60 s window apart from
a baseline" (answer: better than a coin flip, not reliably).

## T3 — Meso forecasting
**First half → second half, within the same meeting** (Spearman, `data/meso_h1_to_h2eventrate.csv`):

| first-half feature | pooled ρ | q (BH-FDR, 3 tests) | team A ρ (p) | team B ρ (p) |
|---|---:|---|---|---|
| **event rate** | **−0.641** | **<.001 \*\*\*** | −0.55 (.023) | −0.66 (.004) |
| baseline entropy | −0.130 | .485 (n.s.) | +0.28 (.27) | −0.47 (.06) |
| %DET median | +0.124 | .485 (n.s.) | −0.08 (.76) | +0.31 (.23) |

**A genuine, robust, direction-consistent finding**: a meeting's first-half reorganization rate
**negatively** predicts its second-half rate (more reorganization early → *less* later, and vice versa),
in **both teams independently** and pooled with q < .001. This reads as within-meeting self-regulation
or a "reorganization budget" rather than momentum — a meeting that has already reorganized a lot in its
first half settles more in its second half. Baseline entropy and %DET level do not forecast the second
half (both n.s.).

**First half → Study 8 outcome ratings** (`data/meso_h1_to_outcomes.csv`, 9 tests, BH-FDR): **0/9 survive
correction** (best: `baseline_entropy` → `issue_resolution_rate`, ρ=−.38, p=.028, q=.19). Consistent with
Study 8's own honest null on whole-meeting predictors — knowing only the first half does not forecast
the meeting's rated outcome any better. Reported alongside Study 8, not instead of it, to avoid
double-publishing the same underlying null.

## T4 — Honest boundary conditions
**Timescale sensitivity** (rank-biserial, W=30/60/90 s; `data/paired_tests_all_windows.csv`):
| feature | W=30 | W=60 | W=90 |
|---|---:|---:|---:|
| entropy_slope | .95 | .94 | .97 |
| det_slope | −.91 | −1.00 | −1.00 |
| switch_rate | 1.00 | 1.00 | 1.00 |
| turnlen_trend | −.67 | −.91 | −.96 |
| question_density | −.87 | −.97 | −.98 |
| gap_trend | −.40 (n.s.) | −.25 (n.s.) | −.12 (n.s.) |

The signature is **stable across a 3× range of pre-event window length** — not an artifact of one
arbitrary window choice. `gap_trend` is consistently the one null feature at every timescale.

**Proportion of events with no detectable precursor** (event's feature vs. that meeting's own baseline
mean±1 SD — a meeting-internal, non-pooled criterion): **72.5%** of events (659/909) show no detectable
`entropy_slope` precursor by this criterion; **51.7%** (457/884) show none on `switch_rate`; **35.1%**
(310/884) show no precursor on *both* signals simultaneously (so 64.9% show a detectable precursor on
at least one). This is fully consistent with, not contradictory to, the T1/T2 results: a real
population-level shift in the mean can coexist with most *individual* events falling inside a
generous ±1 SD band. We read this honestly against the critical-transitions literature: **a majority of
these reorganizations are not reliably "ramped into"** by the measured features — consistent with at
least some being closer to abrupt, discontinuous shifts than to gradually-warned ones. This is not
merely a limitation to be caveated away; it is itself a substantive, theoretically relevant finding
about the character of reorganization.

## Follow-up — which event TYPE has a detectable precursor?
Joining Study 9's event classification (TRANSITION / INTERIOR_HANDOFF / INTERIOR_OTHER — same detector,
deterministic onset match, 909/909 join) onto the pre-event features reveals a clean, coherent pattern:
different event types are anticipatable through **different channels**, and one type is reliably the
least anticipatable of all.

**No-precursor rate by class** (`data/no_precursor_rate_by_class.csv`):
| event class | n | % no `entropy_slope` precursor | % no `switch_rate` precursor | % no precursor on both |
|---|---:|---:|---:|---:|
| TRANSITION | 468 | 72.9% (χ²(2)=0.25, p=.88, n.s.) | **43.3%** (most anticipatable) | 29.1% |
| INTERIOR_HANDOFF | 190 | 71.1% | 58.9% | 38.9% |
| INTERIOR_OTHER | 251 | 72.9% | **61.9%** (least anticipatable) | 39.8% |

The `entropy_slope` no-precursor rate is **flat across event types** (χ²=0.25, p=.88) — the mechanical
approach-to-a-local-extremum pattern doesn't care what kind of event is coming. But `switch_rate`
detectability differs sharply by class (χ²(2)=26.87, **p=1.5e-6**) and so does the combined rate
(χ²=10.96, **p=.004**): **topic/agenda TRANSITIONs are the most anticipatable event type** (only 43%
show no switch-rate precursor), while **INTERIOR_OTHER events are the least** (62% show none).

**Magnitude of the precursor signal by class** (Kruskal-Wallis + pairwise Mann-Whitney, BH-FDR;
`data/precursor_magnitude_by_class.csv`):
| feature | TRANSITION | INTERIOR_HANDOFF | INTERIOR_OTHER | Kruskal-Wallis |
|---|---:|---:|---:|---|
| entropy_slope | 0.15 | **0.22** (steepest) | 0.07 (flattest) | H=21.3, p<.001 |
| det_slope | −0.22 | **−0.26** (steepest) | −0.07 (flattest) | H=22.8, p<.001 |
| switch_rate | **6.73** (highest) | 5.68 | 4.73 (lowest) | H=49.8, p<.001 |
| turnlen_trend | 0.70 | 0.68 | **3.08** (turns lengthening, not shortening) | H=42.8, p<.001 |
| question_density | 0.35 | 0.35 | **0.40** (highest) | H=12.0, p=.002 |

**Reading — two distinct anticipatable "channels," and one abrupt residual class:**
- **Topic/agenda TRANSITIONs** are anticipated mainly through **rising multi-party switching** (highest
  switch_rate of the three, and the lowest no-precursor rate on that feature) — consistent with a group
  audibly winding down or negotiating a topic change through rapid exchange before it happens.
- **Interior floor handoffs** are anticipated mainly through the **cleanest entropy/%DET ramp** (steepest
  slopes of the three classes, even though this channel is largely mechanical) — a floor handoff shows
  the clearest gradual build-up in the reorganization metric itself.
- **INTERIOR_OTHER — the diffuse/residual interior-event category (also the smallest and least
  mechanistically clean category in Study 7's mechanism analysis) — is the least anticipatable event
  type on nearly every measure**: flattest entropy/%DET ramp, lowest switch-rate, highest no-precursor
  rate, and even an inverted turn-length signature (turns *lengthening*, not shortening, beforehand) and
  slightly more questions. This is the closest thing in this corpus to a genuinely abrupt reorganization
  — consistent with T4's finding that a substantial minority of events resist any precursor signature,
  and pointing to *which* events those disproportionately are.

## Leakage audit (as required)
1. **Feature windows are strictly pre-onset.** Every feature is computed over [t_end−W, t_end) with
   t_end = the event onset or baseline pseudo-onset; nothing at or after t_end is used anywhere.
2. **The reorg-event threshold (mean+2.33 SD of RMSE) is computed per meeting, from that meeting's own
   RMSE series only** — an established convention used throughout this program (Studies 2/6/7/9). It
   never pools across meetings, so it cannot leak between the LOMO-CV training and held-out folds by
   construction; T2's requirement ("threshold statistics must be computed excluding the held-out
   meeting") is satisfied automatically, not by an extra step.
3. **Standardization for the classifier is within-meeting** (z-scored using only that meeting's own
   event+baseline rows), applied identically and independently to every meeting, train and test alike —
   no cross-meeting statistic is used for scaling.
4. **The held-out meeting contributes zero rows to model fitting** in its own LOMO-CV fold; only a
   single fixed regularization default (`C=1.0`, no search/tuning) is used throughout.
5. **A subtler, disclosed non-leakage-but-non-causal point**: the event/RMSE threshold for a given
   meeting is computed from that **whole meeting's** RMSE distribution — including seconds after any
   individual event within that same meeting. This does not leak across meetings (point 2), but it does
   mean the event *label* itself is not purely causal/online (an event early in the meeting is labelled
   using a threshold informed by the whole recording). This is the same convention every other study in
   this program uses for event detection, appropriate for **retrospective analysis**, but it is precisely
   why this study is framed as a feasibility probe rather than a specification for a live system — a real
   deployment would need an online/adaptive threshold estimated only from data available so far.
6. **Baseline-matching pool construction** ("≥90 s from every event onset in the meeting") also uses the
   full set of that meeting's event onsets, which is a sampling-design choice, not a feature/label leak:
   it only affects which timepoints are *eligible* to be drawn as a baseline, and is applied identically
   for every meeting.

## Honest interpretation
- **A real, robust, mechanism-independent early-warning signature exists** at the population level:
  rising speaker-switch rate, shortening turns, and fewer questions precede reorganization, replicated
  across 3 window lengths and consistent in direction across nearly all 34 meetings.
- **It is not currently a reliable single-event alarm**: AUC ≈ 0.66 restricted to non-circular features,
  and the majority of individual events show no detectable precursor under a conservative meeting-
  internal criterion. An AUC of this size licenses "there is population-level signal worth building on,"
  not "flag this specific moment as high-risk in real time."
- **A genuine, FDR-surviving meso finding**: within-meeting self-regulation — a reorganization-heavy
  first half predicts a *calmer* second half (ρ=−.64), in both teams. This is new and worth its own
  attention independent of the early-warning framing.
- **First-half dynamics do not forecast meeting-level outcome ratings** (0/9 survive FDR) — consistent
  with, and not double-counting, Study 8's own null.
- **The entropy/%DET-slope "precursor" is largely definitional** and should never be cited alone as
  evidence of a predictive early-warning capability; the behavioral features are the load-bearing,
  non-circular result.
- **What this licenses for practice, stated plainly**: these results support continued investment in
  building and validating an online monitor from turn-taking/text features (a worthwhile next step,
  consistent with Wiltshire's call), but do **not** license claiming a working early-warning tool from
  this analysis alone — that would require online threshold estimation, prospective validation, and a
  much larger, more diverse sample than 2 teams / 34 meetings.

## Honest scope
- 2 teams, 34 meetings — as throughout this program, replication (not generalization) is the standard;
  the T1/T4 meeting-consistency checks and T2's LOMO-CV partially compensate but do not remove this
  limit.
- The classifier uses a single fixed regularization default by design (no tuning), per the guardrail
  against significance/AUC chasing on this sample size — a tuned or ensembled model would likely score
  somewhat higher but that is not the question this feasibility probe is asking.
- `turnlen_trend` and `gap_trend` require ≥3 utterances in the window and so have modestly more missing
  data at the shortest window (W=30 s; see `data/paired_tests_w30.csv` degrees of freedom).
- The 1-SD "no precursor" criterion is one reasonable, disclosed choice; it is not the only way to define
  "detectable," and the exact percentage would shift somewhat under a different threshold (the AUC results
  in T2, using a model-based rather than threshold-based criterion, corroborate the same qualitative
  picture without depending on this specific choice).

## Paper paragraph (drop-in, exact statistics — likely lands in General Discussion / practical implications)
> Answering Wiltshire's (2026) call to move beyond post hoc description, we tested whether
> reorganization events are preceded by a detectable signature. Across 909 events (34 meetings), the
> 60 s window before onset differed from matched, same-stage baselines on 5/6 features (paired,
> per-meeting, BH-FDR; rank-biserial ≈ .91–1.00, stable across 30–90 s windows): rising entropy,
> falling %DET (both partly definitional, approaching a local extremum), and — independent of the
> metric's own construction — rising speaker-switch rate, shortening turns, and fewer questions.
> Restricting to these non-circular, turn-taking/text features, a leave-one-meeting-out classifier
> discriminated pre-event from baseline windows at AUC = 0.66 [95% CI 0.62, 0.70] — real but modest,
> and consistent with 51.7% of individual events showing no detectable single-feature precursor by a
> conservative, meeting-internal criterion. This is the central honest finding: a near-deterministic
> population-level regularity (meeting-level effect sizes near ceiling) coexists with modest single-event
> discriminability, indicating the signature is a real but graded, not-yet-reliable-alarm phenomenon —
> plausibly reflecting a mix of anticipatable and genuinely abrupt reorganizations. A meso-level analysis
> found a meeting's first-half reorganization rate *negatively* predicts its second half (ρ = −.64,
> q < .001, both teams independently), a within-meeting self-regulation effect independent of the
> early-warning question; first-half dynamics did not forecast Study 8's meeting-rating outcomes (0/9
> tests survived FDR), consistent with that study's own null. We read these results as supporting
> continued investment in real-time coordination-support tooling built on turn-taking behavior, not as
> evidence of a currently deployable early-warning system.

## Deliverables
- `src/build_preevent_features.py` → `data/preevent_features{,_w30,_w90}.csv` (event/baseline windows
  at 3 timescales; seeded, reproducible).
- `src/paired_tests.py` → `data/paired_tests_w{30,60,90}.csv`, `data/paired_tests_all_windows.csv`.
- `src/classifier_cv.py` → `data/cv_auc_results.csv`, `data/roc_curves.npz`, `data/single_feature_auc.csv`.
- `src/meso_forecasting.py` → `data/meso_halves.csv`, `data/meso_h1_to_h2eventrate.csv`,
  `data/meso_h1_to_outcomes.csv`.
- `src/null_precursor_rate.py` → `data/no_precursor_summary.csv`, `data/no_precursor_both.csv`.
- `src/precursor_by_class.py` → `data/precursor_by_class.csv`, `data/no_precursor_rate_by_class.csv`,
  `data/precursor_magnitude_by_class.csv`, `data/precursor_magnitude_pairwise_<feature>.csv` (joins
  Study 9's event classification onto the precursor analysis).
- `src/fig_early_warning.py` → `fig_early_warning.{png,pdf,svg}`.
- All data numeric; no verbatim transcript text in any output (question density is a count, not text).

## References
Wiltshire (2026, *Small Group Research*); this program's Studies 2, 6, 7, 8, 9 (event definition,
boundary logic, Study 8 outcome data, established statistical conventions); Scheffer et al. (2009,
critical transitions and early-warning signals in complex systems) for the abrupt-vs-graded framing.
