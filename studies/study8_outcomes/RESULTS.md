# Study 8 — Meeting outcomes: does reorganization matter? (adaptive function, P6)

## Hypothesis
Proposition **P6 (adaptive function)**: teams whose meetings reorganize appropriately rate their
meetings as more effective and convert more decisions into completed action items. The EOS Level 10
protocol these teams run embeds three outcome signals directly in the transcript: a spoken **meeting
rating** (0–10, in the `conclude` stage), **to-do completion** (checked in the *next* meeting's `to-do
review`), and **IDS issue resolution** (closed with an explicit decision in the same meeting).

## Data and extraction
34 meetings (2 teams × ~17), quote-anchored LLM extraction against a written protocol
(`protocol.md`), the same method validated for the L10 stage/anatomy work (Studies 6–7): every
extracted datum carries a verbatim substring, mapped to a timestamp by substring search.

**Coverage / QA** (`QA_SUMMARY.md`, full detail): **582 datums extracted, 581 quote-mapped (99.8%)**,
1 unmappable. Meetings with a spoken rating: **32/34 (94%)** — well above the ~20-meeting threshold for
inferential (not just descriptive) treatment.

**Outcomes** (`data/outcomes_per_meeting.csv`):
| outcome | n | mean | SD | min–max |
|---|---:|---:|---:|---|
| `rating_mean` (0–10, mean of spoken ratings) | 32 | 9.20 | 0.96 | 6.5–10.0 |
| `todo_completion_rate` (%, done=1/partial=0.5/not_done=0, unmentioned excluded from denominator) | 29 | 65.8 | 25.1 | 0–100 |
| `issue_resolution_rate_same_meeting` (%) | 34 | 61.2 | 33.4 | 0–100 |

Ratings are high and left-skewed (near-ceiling: mean 9.2/10) — a real restriction-of-range that will
suppress any correlation with `rating_mean` specifically. To-do completion and issue resolution have
real spread and are the more informative outcomes here. `todo_completion_rate` has n=29 (not 32):
2 meetings are each team's last (no next meeting to check) and 3 further meetings had every to-do
marked "unmentioned" in the next meeting (denominator = 0).

## Predictors
14, **all reused from existing Study 2/6/7 pipeline outputs** — no metric recomputation
(`data/predictors_per_meeting.csv`, `src/build_predictors.py`): `baseline_entropy` (median),
`entropy_sd`, `det_median`, `pct_time_reorganizing`, `reorg_event_rate` (events/10 min),
`mean_event_depth` (entropy excess above baseline, events-weighted), `mean_event_peak_z` (same, in
within-meeting SD units), `boundary_alignment_pct` (share of events within ±30 s of a topic/L10
boundary — reused directly from Study 7's `pct_tr`), plus IDS-only and review-only entropy/%DET/
reorg-rate (from Study 6's `l10_stage_metrics.csv`).

## Method
- **Spearman ρ**, pooled (n = 29–34), Fisher-z 95% CI, **BH-FDR within each outcome family** (14
  predictors); per-team ρ reported descriptively only (n ≈ 14–17/team, underpowered, no correction).
- **Mixed model**: `outcome ~ predictor(z) + week + (1|team)` (statsmodels MixedLM) as a robustness
  check on the Spearman result.
- **Lag**: built into the design — `todo_completion_rate` for meeting *t* is literally the check
  performed in meeting *t+1*, so predictors(t) → outcome already tests the lagged relationship; no
  separate lagged model is needed.
- **Nonlinearity probe**: OLS `outcome ~ x + x²` (inverted-U / requisite-variety check) for
  `reorg_event_rate` and `pct_time_reorganizing` against each outcome.

n is small — effect sizes and CIs are emphasized throughout; p/q are secondary.

## Results

### Headline: no predictor survives multiple-comparison correction, in any outcome, by any method
**0/42** Spearman tests and **0/42** mixed-model tests reach q < .05 within their outcome family.

### The direct adaptive-function proxy (`reorg_event_rate`) is null across all three outcomes
| outcome | ρ | 95% CI | n | p |
|---|---:|---|---:|---:|
| rating_mean | +0.08 | [−0.28, 0.41] | 32 | .68 |
| todo_completion_rate | +0.14 | [−0.24, 0.48] | 29 | .46 |
| issue_resolution_rate | −0.06 | [−0.39, 0.28] | 34 | .72 |

Every CI comfortably spans zero. `mean_event_depth` and `boundary_alignment_pct` (the other two
theoretically central proxies) are equally unremarkable (|ρ| ≤ .31, all n.s.). **Figure 8, panels A–C.**

### The single strongest correlate in the whole grid (flagged, not a finding)
`baseline_entropy` vs `issue_resolution_rate_same_meeting`: **ρ = −0.41, 95% CI [−0.65, −0.08], n = 34,
p = .017, q = .223** (does not survive FDR against the other 13 predictors in that family). Direction:
a **lower** resting baseline entropy (the more consolidated/routinized operating point identified in
Study 5) associates with a **higher** same-meeting issue-resolution rate. This is the largest |ρ| in the
entire 14×3 grid, is directionally coherent with the Study 5 consolidation story, and is shown in
**Figure 8, panel D** for transparency and to motivate future, better-powered work — but by the pre-
registered correction rule it is **not** reported as a significant result.

### Mixed model confirms the null (and exposes a design limitation)
No predictor reaches q < .05 in the `outcome ~ predictor + week + (1|team)` model either
(`data/mixedmodel_results.csv`). **Caveat:** with only **2 teams**, the team random-effect variance is
barely identifiable — 6/42 models returned a singular/degenerate fit (NaN SE). The mixed-model estimates
should be read as roughly OLS-with-week-adjustment, not a fully powered hierarchical test; this is a
structural limitation of a 2-team design, not a bug.

### Nonlinearity probe: no evidence for an inverted-U (requisite-variety) effect
All six quadratic terms are non-significant (p = .19–.78; `data/quadratic_results.csv`); the fitted
"shape" label (U vs inverted-U) flips inconsistently across outcomes, which is itself evidence the
curvature is noise, not signal, at this n. The too-little/too-much-reorganization hypothesis is **not**
supported here — reported as a null, not omitted.

## Honest interpretation
- **P6 is not supported by this test.** Reorganization dynamics (entropy, %DET, event rate/depth,
  boundary alignment — moment-to-moment or stage-conditional) do not predict meeting-level rating,
  to-do completion, or issue resolution at a level that survives correction for 14 simultaneous
  comparisons, in 2 independent statistical approaches (Spearman, mixed model).
- **Power is the binding constraint**, not necessarily the absence of a true effect: n = 29–34 with
  2 clusters gives 95% CIs roughly ±0.3–0.4 wide on every ρ; an effect smaller than |ρ| ≈ .45 is not
  reliably detectable here. The `baseline_entropy` → `issue_resolution` candidate (ρ = −.41) is the
  best-motivated direction for a follow-up with more meetings/teams.
- **Rating has a ceiling problem** (mean 9.2/10): these teams almost never rate a meeting below 6.5, so
  `rating_mean` has little room to correlate with anything. `todo_completion_rate` and
  `issue_resolution_rate` are the more informative outcomes for this kind of test going forward.
- **A design caveat for `todo_completion_rate`:** documented multi-week gaps between some consecutive
  meetings (noted elsewhere in this project) mean a handful of "t → t+1" checks are diluted by
  intervening time/events — flagged in the per-pair extraction prompts, not hidden.
- **Null results are reported as results.** This is a genuine, honestly-powered non-finding for the
  adaptive-function proposition as operationalized here — it does not (yet) earn a place as a positive
  claim in the paper, but the pipeline, data, and null are fully auditable for a future, larger test.

## Paper paragraph (drop-in, exact statistics)
> To test whether reorganization dynamics carry adaptive value (P6), we linked the reorganization
> metrics to three outcomes embedded in the meetings' own EOS Level 10 protocol: a spoken meeting rating
> (0–10; 32/34 meetings), to-do completion (checked in the following meeting; n = 29), and same-meeting
> IDS issue resolution (n = 34), all quote-anchored extractions (99.8% of 582 extracted datums
> verified against the transcript). Across 14 reorganization predictors (entropy, %DET, event rate and
> depth, boundary alignment, and their IDS-only/review-only variants) and all three outcomes, Spearman
> correlations (pooled n = 29–34, BH-FDR within each outcome family) and a `predictor + week + (1|team)`
> mixed model agreed: no predictor survived multiple-comparison correction (0/42 tests, q < .05, either
> method). The direct adaptive-function proxy, reorg-event rate, was null against all three outcomes
> (ρ = +.08, +.14, −.06; all n.s.). The single largest unadjusted correlation, baseline entropy with
> issue-resolution rate (ρ = −.41, 95% CI [−.65, −.08], p = .017), did not survive correction (q = .22)
> and is reported as a candidate for future, better-powered work rather than a finding. A quadratic
> (inverted-U) probe for a requisite-variety effect was also null (all p > .18). We report this
> transparently: at this sample size (34 meetings, 2 teams), reorganization dynamics do not detectably
> predict meeting-level effectiveness outcomes.

## Honest scope
- n = 29–34 meetings, 2 teams — a replication-not-generalization design throughout this program; doubly
  so here, where the outcome layer adds its own extraction noise on top.
- LLM-extracted outcomes are quote-anchored and spot-checked (`QA_SUMMARY.md`) but not yet validated
  against an independent human-coded subset (same caveat as the L10/episode/interior-mechanism work in
  Studies 6–7; Pangakis et al. 2023).
- `rating_mean` is ceiling-restricted; treat `todo_completion_rate` and `issue_resolution_rate` as the
  primary outcomes in any follow-up.
- The mixed model is under-identified with only 2 team clusters — a structural n-of-teams limitation,
  not fixable by more meetings alone.

## Deliverables
- `protocol.md` — extraction protocol (quote-anchored, anti-hallucination rules).
- `annotations/raw/*.json` (34, per-meeting) + `annotations/pairs/*.json` (32, to-do completion
  pairs) — **LOCAL ONLY**, carry verbatim transcript quotes, never published.
- `QA_SUMMARY.md` — extraction QA (counts, mapping rate, spot-check by mapping status; no quote text).
- `data/outcomes_per_meeting.csv`, `data/predictors_per_meeting.csv`, `data/analysis_panel.csv` (merged),
  `data/spearman_results.csv`, `data/spearman_by_team.csv`, `data/mixedmodel_results.csv`,
  `data/quadratic_results.csv` — numeric only, publishable.
- `src/build_predictors.py`, `src/aggregate_outcomes.py`, `src/models.py`, `src/fig_outcomes.py` —
  reproducible end-to-end from raw transcripts + existing Study 2/6/7 metric outputs.
- `fig_outcomes_scatter.{png,pdf,svg}`.

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting); Pangakis et al. (2023, LLM-annotation validation);
Benjamini & Hochberg (1995, FDR).
