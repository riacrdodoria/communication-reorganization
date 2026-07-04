# Study 9 — Who initiates reorganization? (true individual level)

## Terminology correction (important)
Earlier drafts of this study used the word "leader" for the person identified below. **That was
wrong and has been corrected throughout.** These are advisory ("Pulse"-format) meetings, and per this
program's own `METHODS.md` ("Each meeting pairs the team with the same advisor"), the person identified
is very likely **the same external facilitator/advisor across both teams** — not each team's own
internal leader. Every result, label, and column below says **"facilitator"**. This study does **not**
identify or make any claim about either team's own internal leadership structure — see the Honest
interpretation section for what this means for the link to P5.

## Objective
Study 2's "individual vs team-level structure" grouping has so far meant floor *structure*
(participation, centrality) at the individual level, not identifiable *persons*. This study adds the
person level: who triggers reorganization events, whether initiator roles are stable, and whether
initiation shifts toward the external facilitator as teams' relationship with the facilitator matures.
Supports **P3 (multiscale identity)**; see below for the corrected, more cautious relationship to
**P5 (leader-centric consolidation)**.

## Facilitator identification (documented rule)
Per team, the facilitator is the speaker who most often opens the EOS L10 `segue` and `todo`-review
stages (the facilitation role). Raw speaker id **"2" is the modal facilitator of both stages in both
teams** (segue: 35%/47%; todo-review: 36%/62%) — that the *same* raw id is modal in both
independently-numbered teams is itself consistent with a single external advisor running both teams'
sessions, exactly as `METHODS.md` states. `conclude` (a group ritual, not a facilitation act) is not
used and in fact skews to a different speaker in team B. Corroborating check: the facilitator is *not*
the top to-do **owner** in either team (14%/31%, below several other members) — the expected pattern
for an external advisory role that drives structure without doing the team's own delivery work. Full
numbers: `facilitator_identification.md`.

## Method
909 reorganization events (34 meetings; same detector as Studies 2/6/7: RMSE > mean+2.33 SD, contiguous
seconds clustered with an 8 s gap rule). **Three initiator definitions**, computed from raw
utterance timing/speaker/text (no new metrics):
- **`init_primary`** — first speaker, among utterances starting in [onset−5 s, onset+10 s], who differs
  from the *dominant* speaker of the pre-window [onset−15 s, onset) (falls back to `init_floor` if none).
- **`init_floor`** — speaker holding the floor at the exact onset second (Last-Speaker-Holds convention).
- **`init_question`** — first speaker, in the same window, whose utterance contains "?" (54% of events
  have no question in-window — null for the rest).
Speaker ids are pseudonymized `S1, S2, ...` per team by order of first appearance; the facilitator is
flagged.

## Results

### T2 — Distribution & concentration
Initiation is moderately concentrated but **not** dominated by any one member (Gini 0.24–0.37 across
definitions/teams — well short of winner-take-all). **Initiation lift** (share of initiations ÷ share of
talk-time) reveals the interesting asymmetry: the **least-talkative member (S5) initiates far more than
their talk-time predicts in both teams** (lift 1.88 / 1.35), while the single most-talkative
*team* member (S1) has lift < 1 in both teams (0.92 / 0.82) — **talking most does not mean initiating
most**. The **facilitator's lift is close to 1** (0.98 / 1.11) — initiation roughly proportional to
their talk-time, neither over- nor under-triggering. **Figure 9, panel A.**

**Stability** (rank correlation of member initiation counts, first half vs second half of each team's
run): **team-and-definition-dependent**. Team A is stable (ρ = .70–.90 across definitions, nominal
p = .04–.19); **team B is not** (ρ = .20, p = .75 for `init_primary`/`init_floor`; ρ = .70, p = .19 for
`init_question`). Reported plainly: initiator-role stability is **not** a general property of this
system — it holds in one team and not the other.

### T3 — Facilitator vs members
**Permutation test** (1000 seeded runs, null = initiator drawn per-meeting proportional to each member's
talk-time share): the facilitator's observed initiated-event share (28.2–28.3% across `init_primary`/
`init_floor`; 27.1% for `init_question`) sits **squarely inside** the talk-time-weighted null
distribution (null mean 27.4–27.6%, 95% CI ≈ [24–31%]; p = .61–.87, all definitions). **The facilitator
initiates exactly as much as their talk-time predicts — no more, no less.** This is, if anything, an
intuitive null: an external advisor running the meeting format is not expected to be a locus of power
within the team the way an internal leader might be — the absence of an "initiation premium" is
consistent with the facilitator's role being process-neutral rather than agenda-controlling.

**Event class × initiator-type.** The hypothesis that TRANSITION events (agenda control) are
facilitator-initiated while interior handoffs are member-initiated is **not supported** — if anything the
nominal pattern points the other way for `init_primary` (facilitator share: INTERIOR_HANDOFF 33.2% >
INTERIOR_OTHER 30.3% > TRANSITION 25.0%; χ²(2)=5.21, p=.074, not significant), and is flat for
`init_floor` (χ²=0.33, p=.85) and `init_question` (χ²=2.02, p=.36). **Reported as a null, stated plainly
against the pre-registered direction.**

### T4 — Longitudinal (relationship to P5 — corrected framing)
Facilitator-initiated share vs. week, Kendall τ: **pooled τ=+.27 (p=.027)** for `init_primary`, driven
almost entirely by **team B (τ=+.41, p=.021)**; team A is flat and non-significant (τ=+.17, p=.34).
`init_floor` is a weaker echo of the same pattern (pooled τ=+.23, p=.059; team B τ=+.25 n.s., team A
τ=+.18 n.s.). `init_question` shows **no** trend (pooled τ=+.15, p=.22). **Figure 9, panel B.**

**Corrected interpretation.** With "facilitator" now understood to be the same external advisor across
both teams, this trend is **not** direct evidence for P5 (leader-centric *consolidation*, which concerns
a team's *own* internal structure). At most it describes something adjacent: in one team, the external
advisor's interventions increasingly coincide with reorganization moments as the engagement matures —
which could reflect the team deferring more to the facilitator's process control, or simply the
facilitator adapting their style to that team, rather than the team's internal leadership consolidating.
It is weak, present in only one team, and vanishes under the question-based definition. **We do not cite
this as support for P5.** A genuine test of P5 would require identifying each team's own internal leader
(e.g., a founder/lead distinguished from the external advisor) — a natural follow-up this study does not
attempt (see Honest scope).

### T5 — Depth by initiator type
Facilitator-initiated events are **shallower** than member-initiated ones under `init_primary`/
`init_floor` — significant at the event level in **team A** (depth 9.94 vs 13.02, Mann-Whitney p=.007;
and 10.31 vs 12.81, p=.010) but **null in team B** (p=.92 / .78); pooled at the meeting level the
pattern is the same direction but only marginal (paired Wilcoxon p=.063 / .148, n=33–34).
`init_question` shows no consistent direction (pooled p=.90). **Team-dependent, not a general
result** — reported as such.

## Sensitivity across the three initiator definitions (as required)
| test | init_primary | init_floor | init_question |
|---|---|---|---|
| Non-null coverage | 100% | 100% | 54% |
| Facilitator-initiated share (pooled) | 28.2% | 28.3% | 27.1% |
| Permutation test vs talk-time null | p=.686 (n.s.) | p=.608 (n.s.) | p=.872 (n.s.) |
| Event class × initiator-type (χ², df=2) | p=.074 (n.s., wrong-direction trend) | p=.848 (n.s., flat) | p=.364 (n.s., flat) |
| Facilitator share vs week, pooled τ | **+.27 (p=.027)** | +.23 (p=.059) | +.15 (p=.216) |
| Facilitator share vs week, team A τ | +.17 (n.s.) | +.18 (n.s.) | +.15 (n.s.) |
| Facilitator share vs week, team B τ | **+.41 (p=.021)** | +.25 (n.s.) | +.05 (n.s.) |
| Depth: facilitator vs member (team A) | **p=.007** (facilitator shallower) | **p=.010** (facilitator shallower) | p=.283 (n.s.) |
| Depth: facilitator vs member (team B) | p=.922 (n.s.) | p=.776 (n.s.) | p=.279 (n.s.) |
| Stability H1 vs H2, team A ρ | .90 | .87 | .70 |
| Stability H1 vs H2, team B ρ | .20 | .20 | .70 |

**Where conclusions depend on the definition, this is stated plainly throughout:** the longitudinal
facilitator-drift (T4) and the depth asymmetry (T5) both weaken from `init_primary` → `init_floor` →
vanish under `init_question`; only the "facilitator initiates in proportion to talk-time" null result
(T3) is fully definition-invariant.

## Honest interpretation
- **The external facilitator does not initiate reorganization disproportionately** — the strongest, most
  robust, definition-invariant finding here, and consistent with the facilitator being a process-neutral
  outsider rather than a power-holder inside the team.
- **The most consistently disproportionate initiator is the quietest team member**, not the facilitator
  — a genuinely new, coherent observation: rare interventions from low-talk-time members trigger
  reorganization more than their airtime would predict, in both teams, across two of three definitions.
- **This study does not test P5.** P5 (leader-centric consolidation) is about a team's own internal
  leadership; the person identified and tracked here is an external advisor, likely the same individual
  across both teams. The weak, team-B-only, definition-fragile drift toward facilitator-initiation over
  time should **not** be reported as evidence for or against P5. It is reported as its own, more modest
  observation about the facilitator's changing role in one team's meetings.
- **The class × initiator-type hypothesis (facilitator = agenda control, members = interior handoffs) is
  not supported** — the (non-significant) trend nominally runs the other way.
- **Facilitator-initiated events tend to be shallower, but only in team A** — a genuine team-level
  moderation, not a general property.
- **n = 2 teams throughout, and both teams share the same facilitator** — every "pooled" statistic is
  dominated by whichever team happens to show the effect, and the facilitator being constant across
  teams means team-level differences in facilitator-related results reflect the *team's* relationship
  with that one advisor, not two different facilitation styles.
- **A true test of P3/P5 at the internal-leadership level remains open**: identifying each team's own
  internal leader (distinct from the shared external facilitator) is a natural follow-up this study does
  not attempt.

## Paper paragraph (drop-in, exact statistics)
> To move from floor *structure* to identifiable *persons* (P3, multiscale identity), we asked who
> initiates each of 909 reorganization events across 34 meetings, using three convergent definitions
> (first new speaker, floor-holder at onset, first questioner in the surrounding window; the latter
> covering 54% of events). The teams' external facilitator (identified from EOS L10 segue/to-do-review
> patterns, and — per this corpus's design — the same advisor across both teams) initiated reorganization
> in exact proportion to their talk-time: a permutation test against a talk-time-weighted null found no
> facilitator advantage (observed share 27–28% vs. null 27–28%, all p > .6, three definitions). The most
> disproportionate initiator was instead each team's least-talkative member (initiation lift 1.9 and
> 1.4× their talk-time share). A weak drift of initiation toward the facilitator over time (pooled
> Kendall τ = +.27, p = .03) was present in one team (τ = +.41, p = .02) but not the other (τ = +.17,
> n.s.), and vanished under the question-based definition; because the facilitator is external to the
> team, we do not interpret this as evidence for or against leader-centric consolidation (P5), which
> concerns a team's own internal leadership structure — a question this analysis does not address.
> Facilitator-initiated events were shallower than member-initiated ones in one team (p = .007–.010) but
> not the other. The hypothesis that agenda-transition events are facilitator-driven while interior
> handoffs are member-driven was not supported (χ²(2) = 5.21, p = .074, nominal direction opposite to
> predicted). We report all of this with the team-level heterogeneity stated plainly: with only 2 teams
> sharing one facilitator, several of these effects are carried by a single team and should not be read
> as general properties of facilitation or leadership in this dataset.

## Honest scope
- 2 teams, **sharing the same external facilitator** — team-level heterogeneity dominates several
  results (T4, T5); pooled statistics can mask a null-in-one-team pattern, and because the facilitator
  is constant, any "facilitator effect" difference between teams is really a difference in that team's
  relationship with the one advisor, not two facilitation styles.
- `init_question` covers only 54% of events (no question in window for the rest) — its weaker/absent
  effects may partly reflect this reduced, non-random subsample, not only a true absence of signal.
- The "dominant pre-window speaker" and "floor at onset" constructs use the same Last-Speaker-Holds /
  word-count conventions as the rest of this program, for consistency, but have not been validated
  against independent (e.g. human-coded) initiator judgments.
- Facilitator identification is a documented, transparent rule (segue/to-do-review facilitation) but is
  a single per-team categorical label, not a continuous measure, and — as corrected above — identifies
  an external advisor, not either team's own internal leader. Identifying an internal leader is
  unattempted future work.

## Deliverables
- `facilitator_identification.md` — documented facilitator-identification rule, numbers, and the
  terminology correction.
- `src/build_events_initiators.py` → `data/events_initiators.csv` (909 events × 3 initiator definitions,
  event class, depth, pseudonymized speaker/facilitator labels).
- `src/descriptives.py` → `data/talk_time_share.csv`, `data/gini_by_team_definition.csv`,
  `data/initiation_lift.csv`, `data/stability_halves.csv`.
- `src/facilitator_tests.py` → `data/permutation_facilitator_share.csv`, `data/class_by_initiator_type.csv`.
- `src/longitudinal_and_depth.py` → `data/facilitator_share_vs_week.csv`, `data/depth_by_initiator_type.csv`.
- `src/fig_initiators.py` → `fig_initiators.{png,pdf,svg}`.
- All data numeric/pseudonymized; no verbatim transcript text in any output.

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting — facilitator role); this program's `METHODS.md`
("Each meeting pairs the team with the same advisor"); prior Studies 2, 5, 6, 7 of this program (event
definition, EOS stage extraction, consolidation trends, boundary/class logic).
