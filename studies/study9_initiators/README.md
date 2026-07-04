# Study 9 — Who initiates reorganization? (true individual level)

## Terminology note (correction)
Earlier drafts of this study used the word "leader" for the facilitation role identified below. That
was wrong and has been corrected throughout: these are advisory ("Pulse"-format) meetings, and per this
program's own `METHODS.md` ("Each meeting pairs the team with the same advisor"), the person identified
is very likely **the same external facilitator/advisor across both teams** — not either team's own
internal leader. Every output below says **"facilitator"**; this study makes no claim about either
team's own internal leadership structure.

## Rationale and gap
Study 2's individual-vs-team-level framing has, up to now, meant floor *structure* (participation,
centrality) at the individual level — not identifiable *persons*. This study adds the person level: who
triggers reorganization events, whether initiator roles are stable, and whether initiation shifts toward
the external facilitator over time. Supports **P3 (multiscale identity)**; see `RESULTS.md` for why this
study's longitudinal finding is *not* cited as support for **P5 (leader-centric consolidation)**, which
concerns a team's own internal leadership rather than a shared external advisor.

## Method
**Facilitator identification (documented rule).** Per team, the facilitator is the speaker who most
often opens the EOS L10 `segue` and `todo`-review stages (the facilitation role): the modal facilitator
of both stages in both teams — the same raw speaker id in both independently-numbered teams, consistent
with a single external advisor running both teams' sessions. Corroborated (and clarified) by the fact
this facilitator is *not* the top to-do owner in either team — an external advisory role, not "who does
the most work." Full numbers in `facilitator_identification.md`.

**Initiator definitions**, computed from raw utterance timing/speaker/text (no new metrics) for each of
909 reorganization events (34 meetings; same detector as Studies 2/6/7):
- `init_primary` — first speaker, among utterances in [onset−5 s, onset+10 s], who differs from the
  dominant speaker of the pre-window [onset−15 s, onset).
- `init_floor` — speaker holding the floor at the exact onset second (Last-Speaker-Holds convention).
- `init_question` — first speaker asking a question ("?") in the same window (covers 54% of events).

Speaker ids are pseudonymized `S1, S2, ...` per team; the facilitator is flagged. Statistics: Gini
concentration; initiation lift (share of initiations ÷ share of talk-time); rank-stability (Spearman)
across first/second half of each team's run; a talk-time-weighted permutation test (1000 seeded runs)
for facilitator-share; χ² for event-class × initiator-type; Kendall τ for facilitator-share vs. week;
Mann-Whitney / paired Wilcoxon for event depth by initiator type.

## Results
- **The facilitator does not initiate disproportionately.** A permutation test against a talk-time-
  weighted null finds the facilitator's initiated-event share (27–28%, all three definitions) sits
  squarely inside the null distribution (p = .61–.87). **Definition-invariant** — and an intuitive null,
  since an external advisor is not expected to be a within-team locus of power the way an internal
  leader might be.
- **The most disproportionate initiator is each team's least-talkative member**, not the facilitator:
  initiation lift 1.9× and 1.4× their talk-time share in the two teams — rare interventions from
  low-airtime members trigger reorganization more than their talk-time predicts.
- **A weak, team-dependent drift of initiation toward the facilitator over time**: pooled Kendall
  τ = +.27 (p = .03), driven by one team (τ = +.41, p = .02) and absent in the other (τ = +.17, n.s.);
  the trend vanishes under the question-based definition (τ = +.15, n.s.). **Because the facilitator is
  external to the team (and shared across both teams), this is not interpreted as evidence for or
  against P5 (leader-centric consolidation)**, which concerns a team's own internal leadership — a
  question this study does not address.
- **The class × initiator-type hypothesis is not supported** — agenda-transition events are not more
  facilitator-initiated than interior handoffs; if anything the (non-significant) nominal trend runs the
  other way (χ²(2) = 5.21, p = .074).
- **Facilitator-initiated events are shallower, but only in one team** (event-level Mann-Whitney p =
  .007–.010 in team A; null in team B) — a team-level moderation, not a general property.
- **Initiator-role stability is team-dependent**: rank-stable across the run's first/second half in one
  team (ρ = .70–.90) but not the other (ρ = .20–.70 depending on definition).

Full statistics, a definition-sensitivity comparison table, and honest interpretation: `RESULTS.md`.

## Honest scope
- 2 teams **sharing the same external facilitator** — team-level heterogeneity dominates the
  longitudinal and depth results; because the facilitator is constant across teams, any team-to-team
  difference reflects that team's relationship with the one advisor, not two facilitation styles.
- `init_question` covers only 54% of events (no question in-window for the rest); its weaker/absent
  effects may partly reflect this reduced, non-random subsample.
- The floor/dominance constructs reuse this program's established Last-Speaker-Holds and word-count
  conventions for consistency, but have not been validated against independent (e.g. human-coded)
  initiator judgments.
- Facilitator identification is a single documented categorical rule (segue/to-do-review facilitation),
  not a continuous measure — and, as corrected above, identifies an external advisor, not either team's
  own internal leader. Identifying an internal leader (distinct from the shared facilitator) is
  unattempted future work.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_events_initiators.py` | transcripts + Study 2/6/7 metrics, episode & L10 boundaries | `results/events_initiators.csv` | **yes** |
| `descriptives.py` | transcripts + `results/events_initiators.csv` | `results/talk_time_share.csv`, `results/gini_by_team_definition.csv`, `results/initiation_lift.csv`, `results/stability_halves.csv` | **yes** |
| `facilitator_tests.py` | `results/events_initiators.csv`, `results/talk_time_share.csv` | `results/permutation_facilitator_share.csv`, `results/class_by_initiator_type.csv` | no |
| `longitudinal_and_depth.py` | `results/events_initiators.csv` | `results/facilitator_share_vs_week.csv`, `results/depth_by_initiator_type.csv` | no |
| `fig_initiators.py` | `results/initiation_lift.csv`, `results/events_initiators.csv` | `figures/fig_initiators.png/pdf/svg` | no |

All published outputs are numeric and speaker-pseudonymized; no verbatim transcript text appears in any
Study 9 artifact (unlike Studies 6–8, this study needed no quote-anchored LLM extraction at all — every
datum is derived directly from utterance timing, speaker id, and the presence/absence of "?").

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting — facilitator role); this program's `METHODS.md`
("Each meeting pairs the team with the same advisor"); Studies 2, 5, 6, 7 (event definition, EOS stage
extraction, consolidation trends, boundary/class logic). See `references.md`.
