# Study 8 — Meeting outcomes: does reorganization matter? (adaptive function)

## Rationale and gap
Studies 1–7 establish what communication reorganization *is* (an endogenous, supra-autoregressive,
coordination-flavored phenomenon) and *where/how* it lives (topic transitions, floor handoffs, the EOS
Level 10 agenda). None of them ask whether it *matters* — whether reorganization predicts anything
about a meeting's real-world effectiveness. This study adds that outcome layer, testing proposition
**P6 (adaptive function)**: teams whose meetings reorganize appropriately rate their meetings as more
effective and convert more decisions into completed action items.

The EOS Level 10 protocol these teams already run embeds three outcome signals directly in the
transcript: a spoken **meeting rating** (0–10, in the `conclude` stage), **to-do completion** (checked
in the *next* meeting's `to-do review`), and **IDS issue resolution** (closed with an explicit decision
in the same meeting).

## Method
**Outcome extraction** (quote-anchored, same method validated for the L10 stage/interior-mechanism work
in Studies 6–7): one LLM annotator per meeting extracts every spoken rating, every to-do assigned, and
every IDS issue raised/resolved, each carrying a verbatim quote mapped to a timestamp by substring
search. A second pass checks each to-do's status (done/partial/not_done/unmentioned) against the
*next* meeting's transcript — this is the lagged test by construction, since the check literally happens
one meeting later. QA: 581/582 extracted datums quote-mapped (99.8%); rating spoken in 32/34 meetings
(94%) — full inferential treatment, not merely descriptive.

**Predictors** — 14, all reused from the existing Study 2/6/7 pipeline outputs (no metric
recomputation): resting entropy/%DET (median, SD), reorg-event rate and depth (entropy excess above
baseline, and in within-meeting SD units), % time reorganizing, boundary alignment (share of events at a
topic/L10 boundary — reused directly from Study 7), and IDS-only / procedural-review-only versions of
entropy, %DET, and reorg-rate (reused from Study 6).

**Models.** Spearman ρ (pooled, Fisher-z 95% CI, BH-FDR within each outcome family of 14 predictors) and
a `outcome ~ predictor(z) + week + (1|team)` mixed model as a robustness check; an OLS quadratic probe
(`x + x²`) for an inverted-U / requisite-variety effect on the two most direct reorganization-intensity
proxies.

## Results
**No predictor survives multiple-comparison correction, for any outcome, by any method: 0/42 Spearman
tests and 0/36 mixed-model tests reach q < .05** (six mixed models did not converge and are reported as
such, not counted). The direct adaptive-function proxy, reorg-event rate,
is null against all three outcomes (ρ = +.08, +.14, −.06 for rating, to-do completion, and issue
resolution; all n.s., 95% CIs comfortably spanning zero). No unadjusted correlation in the grid reaches
p < .05 on the corrected corpus (largest: IDS reorganization rate vs same-meeting issue resolution,
ρ = +.31, p = .075, q = .46). An earlier version singled out resting baseline entropy vs issue resolution
(ρ = −.41, p = .017) as a candidate; that value was carried by the transcription-tool line that deflated
entropy in the ten latest meetings (`METHODS.md` §1) and is now ρ = −.23 (p = .18). The inverted-U probe
is also null.

**This is a genuine, honestly-powered null result for P6 as tested here.** At n = 29–34 meetings and 2
teams, an effect smaller than |ρ| ≈ .45 is not reliably detectable; the meeting rating outcome is
additionally ceiling-restricted (mean 9.2/10), leaving `todo_completion_rate` and
`issue_resolution_rate` as the more informative outcomes for any follow-up. Full statistics, honest
scope, and a drop-in paper paragraph are in `RESULTS.md`.

## Honest scope
- 2 teams, 29–34 meetings — under-identified for a `(1|team)` random effect (6/42 mixed models returned
  a singular fit); read those estimates as OLS-with-week-adjustment, not a fully powered hierarchical
  test.
- LLM-extracted outcomes are quote-anchored and spot-checked (`QA_SUMMARY.md`) but not yet validated
  against an independent human-coded subset (as with the L10/episode/interior-mechanism annotations in
  Studies 6–7; Pangakis et al. 2023).
- Documented multi-week gaps between some consecutive meetings dilute a handful of the to-do "t→t+1"
  checks; noted, not hidden.
- Null results are reported as results — P6 is not (yet) supported, and is not claimed as a positive
  finding in the paper on the strength of this test.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_predictors.py` | Study 2/6/7 metric & panel outputs | `results/predictors_per_meeting.csv` | no |
| `aggregate_outcomes.py` | transcripts + quote-anchored annotations (local only) | `results/outcomes_per_meeting.csv`, `QA_SUMMARY.md` | **yes** |
| `models.py` | `results/outcomes_per_meeting.csv`, `results/predictors_per_meeting.csv` | `results/analysis_panel.csv`, `results/spearman_*.csv`, `results/mixedmodel_results.csv`, `results/quadratic_results.csv` | no |
| `fig_outcomes.py` | `results/analysis_panel.csv` | `figures/fig_outcomes_scatter.png/pdf/svg` | no |

The per-meeting rating/to-do/issue extractions and the to-do completion pairs carry verbatim transcript
quotes and are withheld with the transcripts, per this repo's privacy policy — only the numeric,
aggregated `results/*.csv` and the QA summary (mapping rates only, no quote text) are published.

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting); Pangakis et al. (2023, LLM-annotation validation);
Benjamini & Hochberg (1995, FDR). See `references.md`.
