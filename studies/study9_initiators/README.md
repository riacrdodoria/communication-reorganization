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
**Facilitator identification (corrected).** The facilitator's raw `speaker_id` is resolved **per
meeting** (not a single constant — an earlier version of this study hardcoded raw id "2" for all 34
meetings, which is wrong for 24/34 of them, since raw ids are assigned per meeting by order of first
appearance and are not a persistent cross-meeting identity). The corrected per-meeting mapping is
verified against the researcher's own retained, unpublished name-labeled source transcripts, 100%
internally consistent within every meeting. Corroborated by the fact this facilitator is *not* the top
to-do owner in either team — an external advisory role, not "who does the most work." Full numbers and
the correction's rationale: `facilitator_identification.md`.

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
- **The facilitator initiates significantly *less* than their talk-time predicts.** A permutation test
  against a talk-time-weighted null finds the facilitator's initiated-event share (36–51% across the
  three definitions) falls significantly *below* the null distribution (p < .0001, p = .004, p = .002).
  **Definition-invariant, and a reversal of this study's original (uncorrected) result**, which had
  reported the facilitator at chance (p = .61–.87) under a since-corrected identification rule — see
  `facilitator_identification.md`.
- **The most disproportionate initiator is each team's least-talkative member**, not the facilitator:
  initiation lift 1.9× and 1.4× their talk-time share in the two teams — rare interventions from
  low-airtime members trigger reorganization more than their talk-time predicts. Together with the
  corrected facilitator result above, both ends of the talk-time distribution point the same way: away
  from proportional initiation by the most central/authoritative voice.
- **A weak, team-B-dominated drift of initiation toward the facilitator over time**: pooled Kendall
  τ = +.20 (p = .105, n.s.) for the primary definition, τ = +.32 (p = .009) for the floor definition —
  both driven by one team (τ = +.54, p = .003) with the other team flat or slightly negative; the trend
  vanishes under the question-based definition. **Because the facilitator is external to the team (and
  shared across both teams), this is not interpreted as evidence for or against P5 (leader-centric
  consolidation)**, which concerns a team's own internal leadership — a question this study does not
  address.
- **The class × initiator-type hypothesis is not supported** — agenda-transition events are not more
  facilitator-initiated than interior handoffs (χ²(2) = 1.96–4.55, all p > .10 across definitions).
- **The previously reported "facilitator-initiated events are shallower in one team" finding does not
  survive the identification correction and is withdrawn** — with the corrected facilitator identity,
  depth by initiator type is null in both teams, all definitions (p = .10–.77).
- **Initiator-role stability is team-dependent**: rank-stable across the run's first/second half in one
  team (ρ = .70–.90) but not the other (ρ = .20–.70 depending on definition). Unaffected by the
  facilitator correction.

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
- Facilitator identification is a documented per-meeting categorical rule (corrected from an earlier,
  wrong constant-id version — see `facilitator_identification.md`), not a continuous measure — and
  identifies an external advisor, not either team's own internal leader. Identifying an internal leader
  (distinct from the shared facilitator) is unattempted future work.
- This correction changed three results materially: the facilitator-vs-null test reversed from null to
  significantly below-null; the pooled longitudinal trend lost significance under one definition and
  gained it under another; the team-A depth asymmetry did not survive and is withdrawn. The
  quiet-member-lift, Gini, and stability results were unaffected.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `build_events_initiators.py` | transcripts + Study 2/6/7 metrics, episode & L10 boundaries + `data/facilitator_raw_id_verified.csv` | `results/events_initiators.csv` | **yes** |
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
