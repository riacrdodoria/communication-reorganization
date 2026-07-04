# Study 9 — Who initiates reorganization? (true individual level)

## Rationale and gap
Study 2's individual-vs-team-level framing has, up to now, meant floor *structure* (participation,
centrality) at the individual level — not identifiable *persons*. This study adds the person level: who
triggers reorganization events, whether initiator roles are stable, and whether initiation shifts toward
the leader as teams consolidate. Supports **P3 (multiscale identity)** and enriches **P5 (leader-centric
consolidation)**.

## Method
**Leader identification (documented rule).** Per team, the leader is the speaker who most often opens
the EOS L10 `segue` and `todo`-review stages (the facilitator role): the modal facilitator of both
stages in both teams, corroborated (and nuanced) by the fact this facilitator is *not* the top to-do
owner in either team — a facilitator/advisor role, not necessarily "who does the most work." Full
numbers in `leader_identification.md`.

**Initiator definitions**, computed from raw utterance timing/speaker/text (no new metrics) for each of
909 reorganization events (34 meetings; same detector as Studies 2/6/7):
- `init_primary` — first speaker, among utterances in [onset−5 s, onset+10 s], who differs from the
  dominant speaker of the pre-window [onset−15 s, onset).
- `init_floor` — speaker holding the floor at the exact onset second (Last-Speaker-Holds convention).
- `init_question` — first speaker asking a question ("?") in the same window (covers 54% of events).

Speaker ids are pseudonymized `S1, S2, ...` per team; the leader is flagged. Statistics: Gini
concentration; initiation lift (share of initiations ÷ share of talk-time); rank-stability (Spearman)
across first/second half of each team's run; a talk-time-weighted permutation test (1000 seeded runs)
for leader-share; χ² for event-class × initiator-type; Kendall τ for leader-share vs. week; Mann-Whitney
/ paired Wilcoxon for event depth by initiator type.

## Results
- **The leader does not initiate disproportionately.** A permutation test against a talk-time-weighted
  null finds the leader's initiated-event share (27–28%, all three definitions) sits squarely inside the
  null distribution (p = .61–.87). **Definition-invariant.**
- **The most disproportionate initiator is each team's least-talkative member**, not the leader:
  initiation lift 1.9× and 1.4× their talk-time share in the two teams — rare interventions from
  low-airtime members trigger reorganization more than their talk-time predicts.
- **A weak, team-dependent drift of initiation toward the leader over time**: pooled Kendall τ = +.27
  (p = .03), driven by one team (τ = +.41, p = .02) and absent in the other (τ = +.17, n.s.); the trend
  vanishes under the question-based definition (τ = +.15, n.s.). Reported as suggestive support for
  leader-centric consolidation (P5), not a robust cross-team effect.
- **The class × initiator-type hypothesis is not supported** — agenda-transition events are not more
  leader-initiated than interior handoffs; if anything the (non-significant) nominal trend runs the
  other way (χ²(2) = 5.21, p = .074).
- **Leader-initiated events are shallower, but only in one team** (event-level Mann-Whitney p = .007–
  .010 in team A; null in team B) — a team-level moderation, not a general property.
- **Initiator-role stability is team-dependent**: rank-stable across the run's first/second half in one
  team (ρ = .70–.90) but not the other (ρ = .20–.70 depending on definition).

Full statistics, a definition-sensitivity comparison table, and honest interpretation: `RESULTS.md`.

## Honest scope
- 2 teams — team-level heterogeneity dominates the longitudinal and depth results; several effects are
  carried by a single team and are stated as such, not generalized.
- `init_question` covers only 54% of events (no question in-window for the rest); its weaker/absent
  effects may partly reflect this reduced, non-random subsample.
- The floor/dominance constructs reuse this program's established Last-Speaker-Holds and word-count
  conventions for consistency, but have not been validated against independent (e.g. human-coded)
  initiator judgments.
- Leader identification is a single documented categorical rule (segue/to-do-review facilitation), not a
  continuous measure of "leadership."

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_events_initiators.py` | transcripts + Study 2/6/7 metrics, episode & L10 boundaries | `results/events_initiators.csv` | **yes** |
| `descriptives.py` | transcripts + `results/events_initiators.csv` | `results/talk_time_share.csv`, `results/gini_by_team_definition.csv`, `results/initiation_lift.csv`, `results/stability_halves.csv` | **yes** |
| `leader_tests.py` | `results/events_initiators.csv`, `results/talk_time_share.csv` | `results/permutation_leader_share.csv`, `results/class_by_initiator_type.csv` | no |
| `longitudinal_and_depth.py` | `results/events_initiators.csv` | `results/leader_share_vs_week.csv`, `results/depth_by_initiator_type.csv` | no |
| `fig_initiators.py` | `results/initiation_lift.csv`, `results/events_initiators.csv` | `figures/fig_initiators.png/pdf/svg` | no |

All published outputs are numeric and speaker-pseudonymized; no verbatim transcript text appears in any
Study 9 artifact (unlike Studies 6–8, this study needed no quote-anchored LLM extraction at all — every
datum is derived directly from utterance timing, speaker id, and the presence/absence of "?").

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting — facilitator/leader role); this program's Studies 2, 5,
6, 7 (event definition, EOS stage extraction, consolidation trends, boundary/class logic). See
`references.md`.
