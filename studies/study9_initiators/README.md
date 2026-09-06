# Study 9 — Who initiates reorganization? (person level)

## Terminology note
These are advisory ("Pulse"-format) meetings; the person analysed as *facilitator* below is **the same
external advisor in every meeting of both teams** (`METHODS.md` §1), not either team's own internal
leader. This study makes no claim about the teams' internal leadership structure.

## Corrections (read first)
This study was rebuilt twice in 2026-09. **(1)** An earlier version identified the facilitator by a single
constant anonymous `speaker_id` ("2") in all 34 meetings. Because `speaker_id` is assigned per meeting by
order of first appearance, that constant was wrong in 24/34 meetings (`facilitator_identification.md`).
**(2)** The same per-meeting labelling had also been used to follow *members* across meetings (initiation
lift, rank stability, "quietest member"); those statistics were therefore comparing labels, not persons.
Every person-level statistic now uses the verified per-meeting role map (`results/speaker_roles_verified.csv`,
`src/roles.py`: FACILITATOR, A1–A3, B1–B3, DEVICE). The corpus was also cleaned of a transcription-tool
line in ten meetings (`METHODS.md` §1), which changes the event set slightly (913 events instead of 909).

## Rationale and gap
Study 2's individual-vs-team-level framing has, up to now, meant floor *structure* (participation,
centrality) at the individual level — not identifiable *persons*. This study adds the person level: who
triggers reorganization events, whether initiator roles are stable, and whether initiation shifts toward
the external facilitator over time. Supports **P3 (multiscale identity)**; the longitudinal result is not
read as support for **P5 (leader-centric consolidation)**, which concerns a team's own internal
leadership rather than a shared external advisor.

## Method
**Events.** 913 reorganization events (34 meetings; RMSE > mean + 2.33 SD, 8 s clustering; trigger class
from the shared rule `src/reorg_events.py`: 468 TRANSITION / 275 INTERIOR_HANDOFF / 170 INTERIOR_OTHER;
the earlier Study-9-specific rule is kept as `event_class_s9rule` for sensitivity).

**Initiator definitions**, computed from utterance timing/speaker/text (no new metrics):
- `init_primary` — first speaker, among utterances in [onset−5 s, onset+10 s], who differs from the
  dominant speaker of the pre-window [onset−15 s, onset) (falls back to `init_floor` if none).
- `init_floor` — speaker holding the floor at the exact onset second (Last-Speaker-Holds convention).
- `init_question` — first speaker asking a question ("?") in the same window (54 % of events).

**Speaker labels** are the verified roles. Statistics: Gini concentration; initiation lift (share of
initiations ÷ share of talk-time, word-count based, per person pooled over the team's 17 meetings);
rank stability (Spearman) across the first/second half of each team's run; a talk-time-weighted
permutation test (1,000 seeded runs; p reported as (b+1)/(N+1), floor p < .002) for the facilitator's share;
χ² for event class × initiator type; Kendall τ for facilitator share vs week; Mann–Whitney / paired
Wilcoxon for event depth by initiator type.

## Results
- **Concentration is moderate and similar across teams.** Gini of initiations per person: 0.24 / 0.22
  (`init_primary`), 0.27 / 0.26 (`init_floor`), 0.36 / 0.36 (`init_question`) for Teams A / B. The
  facilitator is the single most frequent initiator in absolute terms (40 % / 33 % of `init_primary`
  events) — but they also hold 46 % / 44 % of the talk-time.
- **The facilitator opens the floor *less* than talk-time predicts, but asks the opening question
  *more*.** Talk-time-weighted permutation null for the facilitator's share of initiated events:
  `init_primary` observed .359 vs null .444 [.415, .475], p < .002; `init_floor` .393 vs .443
  [.413, .474], p < .002; `init_question` **.502 vs .447 [.407, .488], p = .008 — above the null**.
  Lifts: facilitator 0.86 / 0.75 (`init_primary`), 0.95 / 0.81 (`init_floor`), 1.16 / 1.09
  (`init_question`). The facilitator's initiations are questions; the floor-taking and topic-opening moves
  that start a reorganization belong disproportionately to members.
- **The least-talkative member over-initiates in both teams.** `init_primary` lift 1.38 (A3, 7.6 % of
  talk-time) and 1.29 (B2, 8.9 %); the largest lift in Team B is B3 (1.75, 9.9 % talk-time). The
  most-talkative member sits at ≈1.0 / 0.91.
- **Initiator ranks are stable.** First vs second half of each team's run, Spearman ρ = .80 / .90
  (`init_primary`), 1.00 / 1.00 (`init_floor` and `init_question`). The earlier "Team A stable, Team B
  unstable" contrast (ρ .90 vs .20) was a label artefact of per-meeting pseudonyms.
- **Event class does not depend on who initiates.** χ²(2) = 2.8 / 3.6 / 1.8 (p = .24 / .16 / .40) for the
  three definitions; the facilitator initiates 34–40 % of each class.
- **Facilitator share vs week.** Kendall τ = −0.08 (A, p = .65) and +0.52 (B, p = .004) for
  `init_primary`; +0.15 / +0.33 (`init_floor`, pooled +0.27, p = .03); −0.25 / +0.21 (`init_question`).
  Team-dependent; not read as a P5 result (external facilitator).
- **Event depth does not depend on initiator type.** Facilitator- vs member-initiated events differ by
  < 1 %MaxEnt in depth on every definition (meeting-level paired Wilcoxon p = .33–.57).

## Interpretation
The external facilitator drives the *procedure* of the meeting (they hold nearly half the talk-time and
ask the opening question at half of the question-marked events) but the floor-taking act that begins a
reorganization is disproportionately a member's — and especially the quietest member's. Reorganization
is not something the facilitator does *to* the team; it is something members do, with the facilitator's
questions as one of its cues.

## Honest scope
Two teams, one facilitator: the facilitator effect is a single person's style and cannot be generalised.
The "quietest member" is the person with the least talk-time over 17 meetings; the DEVICE role in Team B
(a participant on a shared room device) is treated as one person because their utterances were labelled
as one source. The permutation null conditions on per-meeting talk-time shares; a person who talks a lot
*because* they initiate a lot would depress their own lift. The handoff/other split is rule-sensitive
(`METHODS.md` §4) but no result here conditions on it.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_events_initiators.py` | transcripts + Study 2/6/7 metrics, episode & L10 boundaries + `results/facilitator_raw_id_verified.csv` + `results/speaker_roles_verified.csv` | `results/events_initiators.csv` | **yes** |
| `descriptives.py` | transcripts + `results/events_initiators.csv` | `results/talk_time_share.csv`, `results/gini_by_team_definition.csv`, `results/initiation_lift.csv`, `results/stability_halves.csv` | **yes** |
| `facilitator_tests.py` | `results/events_initiators.csv`, `results/talk_time_share.csv` | `results/permutation_facilitator_share.csv`, `results/class_by_initiator_type.csv` | no |
| `longitudinal_and_depth.py` | `results/events_initiators.csv` | `results/facilitator_share_vs_week.csv`, `results/depth_by_initiator_type.csv` | no |
| `fig_initiators.py` | `results/initiation_lift.csv`, `results/events_initiators.csv` | `figures/fig_initiators.png/pdf/svg` | no |

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting — facilitator role); this program's `METHODS.md`
("Each meeting pairs the team with the same advisor"); Studies 2, 5, 6, 7 (event definition, EOS stage
extraction, boundary/class logic). See `references.md`.
