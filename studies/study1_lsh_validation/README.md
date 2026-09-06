# Study 1 — Validation of the Last-Speaker-Holds representation

## Rationale
All later studies compute reorganization metrics on a turn-taking series. A practical question precedes
them: how should silence and floor gaps be represented? The **Last-Speaker-Holds (LSH)** representation
carries the most recent floor-taker forward through silence, preserving floor-holding continuity, rather
than treating every gap as a distinct "silence" state. Before relying on LSH we verify that it does not
distort the construct relative to the **standard** active-speaker representation that keeps silence and
gaps as separate states.

## Method
For each meeting we build both representations of the second-by-second speaker series and compute the
reorganization metrics (entropy, %DET, RMSE; `src/gorman_reimpl.py`) on each. We then correlate the LSH
and standard metric trajectories within meeting and across validation sessions. This is a convergent-
validity check: high agreement means LSH is a faithful, simpler substrate.

## Result
The LSH and standard representations yield essentially the same reorganization metrics. **Provenance
(clarified 2026-09-05):** the convergent-validity figure **r ≈ .87–.93** was obtained on Gorman and
colleagues' published validation corpora (submarine crews, mean r = .93; surgical teams, mean r = .89)
with an earlier 1 Hz implementation of the metrics (61 s window, raw bits), not on the present 34
meetings. On the present corpus, with the Gorman-faithful metrics of `src/gorman_reimpl.py`, the
correlation between the entropy trajectory of the multi-speaker state series and that of the same series
with the last state carried forward through silences is **median r = .94** (min .90; `figures/`
`fig_paper_S1_lsh_validation.png`, `paper_figures/fig_paper_S1.py`). LSH is therefore adopted as the
turn-taking substrate throughout.

## Notes
- This is a methodological validation, not a substantive claim about teams.
- The %DET saturation issue (a property of 1 s onset resolution, addressed via L_min = 8 in Study 2) is
  independent of the LSH-vs-standard equivalence.

## Files
- `src/gorman_reimpl.py` (repository root `src/`) — constructs the team-state series and the three
  metrics used here and in every subsequent study.

## References
Gorman, Cooke, Amazeen & Fouse (2012); Cooke, Gorman, Myers & Duran (2013). See `references.md`.
