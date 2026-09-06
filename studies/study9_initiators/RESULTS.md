# Study 9 — Who initiates reorganization? (person level) — results

All numbers below are from the corrected pipeline (2026-09-05): transcription-tool line removed from ten
meetings (`METHODS.md` §1), facilitator identified per meeting, members tracked by verified role
(`results/speaker_roles_verified.csv`), trigger classes from the shared rule (`src/reorg_events.py`).
Superseded numbers from earlier versions are not repeated here; the corrections are described in
`README.md` and `facilitator_identification.md`.

## Objective
Add the person level to the program: who triggers reorganization events; whether initiator roles are
stable; whether initiation shifts toward the external facilitator over time; whether who initiates
changes the kind or depth of the event.

## Method
913 reorganization events, 34 meetings (RMSE > mean + 2.33 SD, 8 s clustering; 468 TRANSITION /
275 INTERIOR_HANDOFF / 170 INTERIOR_OTHER). Three initiator definitions (`init_primary`, `init_floor`,
`init_question`; see `README.md`). Talk-time share = words per person / words in the meeting, pooled over
each team's 17 meetings for the lift ratio. Permutation null for the facilitator's share: for every event,
draw an initiator from that meeting's participants with probability proportional to their talk-time share
in that meeting; 1,000 seeded draws; two-sided p = (b + 1)/(N + 1).

## Results

### T2 — Distribution and concentration
| definition | team | events | FACILITATOR | members (desc.) | Gini |
|---|---|---:|---:|---|---:|
| init_primary | A | 429 | 170 | A1 121, A2 93, A3 45 | 0.235 |
| init_primary | B | 484 | 158 | B1 124, B3 84, DEVICE 62, B2 56 | 0.220 |
| init_floor | A | 429 | 188 | A1 115, A2 84, A3 42 | 0.273 |
| init_floor | B | 484 | 171 | B1 127, B3 77, B2 57, DEVICE 52 | 0.255 |
| init_question | A | 233 | 124 | A1 52, A2 40, A3 17 | 0.357 |
| init_question | B | 261 | 124 | B1 48, B3 43, B2 28, DEVICE 18 | 0.356 |

### T2b — Initiation lift (share of initiations ÷ share of talk-time), `init_primary`
| team | person | init share | talk share | lift |
|---|---|---:|---:|---:|
| A | FACILITATOR | .396 | .461 | **0.86** |
| A | A1 | .282 | .283 | 1.00 |
| A | A2 | .217 | .180 | 1.21 |
| A | A3 (least talk) | .105 | .076 | **1.38** |
| B | FACILITATOR | .326 | .435 | **0.75** |
| B | B1 | .256 | .283 | 0.91 |
| B | B2 (least talk) | .116 | .089 | **1.29** |
| B | DEVICE | .128 | .094 | 1.37 |
| B | B3 | .174 | .099 | 1.75 |

`init_floor`: facilitator 0.95 / 0.81; least-talkative 1.29 / 1.32. `init_question`: facilitator **1.16 /
1.09** (the only definition on which the facilitator over-initiates); least-talkative 0.96 / 1.20.

### T3 — Facilitator vs talk-time-weighted null
| definition | n | observed share | null mean | null 95 % | p |
|---|---:|---:|---:|---|---|
| init_primary | 913 | .359 | .444 | [.415, .475] | < .002 (below) |
| init_floor | 913 | .393 | .443 | [.413, .474] | < .002 (below) |
| init_question | 494 | .502 | .447 | [.407, .488] | .008 (**above**) |

Event class × initiator type (facilitator vs member): χ²(2) = 2.82 (p = .24), 3.64 (p = .16), 1.84
(p = .40) for the three definitions. Facilitator share by class (`init_primary`): TRANSITION 33.5 %,
INTERIOR_HANDOFF 39.6 %, INTERIOR_OTHER 36.5 %.

### T2c — Rank stability (first vs second half of each team's run, Spearman ρ)
| definition | Team A | Team B |
|---|---:|---:|
| init_primary | .80 (p = .20) | .90 (p = .04) |
| init_floor | 1.00 | 1.00 |
| init_question | 1.00 | 1.00 |

(With 4–5 persons per team the p-values are uninformative; the point is that the ordering is preserved
in both teams on every definition. The earlier ρ = .90 vs .20 contrast compared per-meeting labels, not
persons, and is withdrawn.)

### T4 — Facilitator share vs week (Kendall τ, per-meeting share)
| definition | Team A | Team B | pooled |
|---|---|---|---|
| init_primary | −0.08 (p = .65) | +0.52 (p = .004) | +0.21 (p = .09) |
| init_floor | +0.15 (p = .41) | +0.33 (p = .06) | +0.27 (p = .03) |
| init_question | −0.25 (p = .16) | +0.21 (p = .23) | +0.03 (p = .78) |

Team-dependent (Study 11 flags `facilitator_share_vs_week_tau` as significant in one team only). Not
evidence for or against P5: the facilitator is an external advisor, not either team's own leader.

### T5 — Event depth by initiator type (entropy at event minus meeting baseline, %MaxEnt)
| definition | facilitator | member | meeting-level paired Wilcoxon |
|---|---:|---:|---|
| init_primary | 12.6 | 13.2 | p = .57 |
| init_floor | 12.6 | 13.6 | p = .55 |
| init_question | 14.3 | 15.0 | p = .33 |

## Honest interpretation
Talk-time explains most of who initiates; the residual is *anti*-facilitator on the floor-taking
definitions and *pro*-facilitator on the question definition. The consistent over-initiator is the
least-talkative member (both teams, two of three definitions). Initiator roles are stable within each
team's run. Who initiates does not change what kind of event follows, nor how deep it is.

## Paper paragraph (drop-in)
> Across 913 reorganization events, the external facilitator — present in every meeting of both teams
> and holding 44–46 % of the talk-time — initiated fewer floor-taking and topic-opening events than a
> talk-time-weighted null predicts (observed share .36 and .39 vs null .44; permutation p < .002 for both
> definitions; lift 0.86 and 0.75 in the two teams), but more question-initiated events (.50 vs .45,
> p = .008). The least-talkative member of each team initiated 1.3–1.4× their talk-time share, and
> initiator rankings were stable across the first and second halves of each team's run (Spearman ρ ≥ .80
> on all definitions). Event class and event depth did not depend on initiator type.

## Deliverables
`results/events_initiators.csv` (913 rows; per event: meeting, week, onset, class under both rules,
depth, the three initiators as roles, facilitator flags), `results/talk_time_share.csv`,
`results/gini_by_team_definition.csv`, `results/initiation_lift.csv`, `results/stability_halves.csv`,
`results/permutation_facilitator_share.csv`, `results/class_by_initiator_type.csv`,
`results/facilitator_share_vs_week.csv`, `results/depth_by_initiator_type.csv`,
`figures/fig_initiators.{png,pdf,svg}`.

## References
Wickman (2011); Phipson & Smyth (2010); this program's `METHODS.md`; Studies 2, 6, 7. See `references.md`.
