# Study 9 — Who initiates reorganization? (true individual level)

## Terminology correction (important)
Earlier drafts of this study used the word "leader" for the person identified below. **That was
wrong and has been corrected throughout.** These are advisory ("Pulse"-format) meetings, and per this
program's own `METHODS.md` ("Each meeting pairs the team with the same advisor"), the person identified
is very likely **the same external facilitator/advisor across both teams** — not each team's own
internal leader. Every result, label, and column below says **"facilitator"**. This study does **not**
identify or make any claim about either team's own internal leadership structure — see the Honest
interpretation section for what this means for the link to P5.

## Identification-method correction (important — supersedes the original numbers in this section)
The original version of this study identified the facilitator by a **single constant raw `speaker_id`
("2") applied to all 34 meetings**, chosen as the modal (most common) opener of the `segue`/`todo` L10
stages pooled across each team's 17 meetings. That was methodologically unsound: raw `speaker_id` in
this corpus is assigned **per meeting**, by order of first appearance in that specific transcript — it
is not a persistent identity across meetings, so a single constant cannot correctly identify the same
real person in more than a fraction of meetings by construction.

The facilitator's raw `speaker_id` is now resolved **per meeting**, verified against the researcher's
own retained, name-labeled source transcripts (never published — no name appears anywhere in this
repository). Verification aligned each meeting's name-labeled transcript to its anonymized counterpart
utterance-for-utterance (exact line-count match confirms alignment) and found the facilitator's identity
**100% internally consistent within every one of the 34 meetings**. Corrected distribution: raw
`speaker_id` **"1" in 23 meetings, "2" in 10, "3" in 1**. The original constant ("2") was therefore
correct in only 10/34 meetings (29%) and wrong in the other **24/34 (71%)**. See
`facilitator_identification.md` for full detail. Every result below reflects the corrected
identification; where a result changed materially from the original (uncorrected) version, that is
stated explicitly.

## Objective
Study 2's "individual vs team-level structure" grouping has so far meant floor *structure*
(participation, centrality) at the individual level, not identifiable *persons*. This study adds the
person level: who triggers reorganization events, whether initiator roles are stable, and whether
initiation shifts toward the external facilitator as teams' relationship with the facilitator matures.
Supports **P3 (multiscale identity)**; see below for the corrected, more cautious relationship to
**P5 (leader-centric consolidation)**.

## Method
909 reorganization events (34 meetings; same detector as Studies 2/6/7: RMSE > mean+2.33 SD, contiguous
seconds clustered with an 8 s gap rule). **Three initiator definitions**, computed from raw
utterance timing/speaker/text (no new metrics):
- **`init_primary`** — first speaker, among utterances starting in [onset−5 s, onset+10 s], who differs
  from the *dominant* speaker of the pre-window [onset−15 s, onset) (falls back to `init_floor` if none).
- **`init_floor`** — speaker holding the floor at the exact onset second (Last-Speaker-Holds convention).
- **`init_question`** — first speaker, in the same window, whose utterance contains "?" (54% of events
  have no question in-window — null for the rest).
Speaker ids are pseudonymized `S1, S2, ...` per team **per meeting** by order of first appearance; the
facilitator is flagged using the corrected per-meeting raw-id lookup above.

## Results

### T2 — Distribution & concentration (unaffected by the correction)
Initiation is moderately concentrated but **not** dominated by any one member (Gini 0.24–0.37 across
definitions/teams — well short of winner-take-all). **Initiation lift** (share of initiations ÷ share of
talk-time) reveals the interesting asymmetry: the **least-talkative member initiates far more than
their talk-time predicts in both teams** (lift 1.87 / 1.35), while the single most-talkative
*team* member has lift < 1 in both teams (0.92 / 0.82) — **talking most does not mean initiating
most**. This part of the story is unchanged by the facilitator-identification fix, since it concerns
non-facilitator members. **Figure 9, panel A.**

**The facilitator's own lift changed with the correction**: 0.98 → **0.98 (team A, unchanged)** but
1.11 → **0.82 (team B, reversed from mildly over-initiating to under-initiating)** — consistent with
the corrected permutation test below.

**Stability** (rank correlation of member initiation counts, first half vs second half of each team's
run; unaffected by the facilitator correction, since it concerns the whole member ranking): **team-and-
definition-dependent**. Team A is stable (ρ = .70–.90 across definitions, nominal p = .04–.19); **team B
is not** (ρ = .20, p = .75 for `init_primary`/`init_floor`; ρ = .70, p = .19 for `init_question`).
Reported plainly: initiator-role stability is **not** a general property of this system — it holds in
one team and not the other.

### T3 — Facilitator vs members (**materially changed by the correction**)
**Permutation test** (1000 seeded runs, null = initiator drawn per-meeting proportional to each member's
talk-time share): with the corrected facilitator identity, the observed initiated-event share
(**36.0% `init_primary`, 39.6% `init_floor`, 51.2% `init_question`**) sits **significantly below** the
talk-time-weighted null (null mean 44.3–44.7%; **p < .0001, p = .004, p = .002** respectively — all
three definitions, all significant). This reverses the original (uncorrected) result, which had reported
the facilitator's share as statistically indistinguishable from the null (p = .61–.87). **The corrected
finding: the facilitator initiates significantly less than their talk-time would predict, in all three
definitions.** Read together with T2, this sharpens rather than complicates the paper's bottom-up
reading: the facilitator (an authority-adjacent role) under-triggers reorganization relative to airtime,
while the quietest team members over-trigger it — the same asymmetry from both ends.

**Event class × initiator-type.** The hypothesis that TRANSITION events (agenda control) are
facilitator-initiated while interior handoffs are member-initiated remains **not supported** after the
correction: `init_primary` χ²(2) = 1.96, p = .375; `init_floor` χ²(2) = 4.55, p = .103; `init_question`
χ²(2) = 2.51, p = .285 — none significant (the specific chi-square values changed from the uncorrected
version, but the conclusion — no significant class dependence — is unchanged).

### T4 — Longitudinal (relationship to P5 — corrected framing, **numbers changed**)
Facilitator-initiated share vs. week, Kendall τ, with the corrected identification: `init_primary`
**pooled τ = +.20 (p = .105, no longer significant** — was τ = +.27, p = .03 in the uncorrected version),
driven by **team B (τ = +.54, p = .003, stronger than before)**; team A is now **slightly negative and
non-significant (τ = −.13, p = .48**, versus a small positive n.s. before). `init_floor` pooled is now
**significant (τ = +.32, p = .009)**, driven again by team B (τ = +.35, p = .053) with team A positive
but weaker (τ = +.23, p = .20). `init_question` shows **no** trend (pooled τ = +.09, p = .48). **Figure
9, panel B (regenerated with corrected data).**

**Corrected interpretation.** The qualitative picture is similar to before — a weak, team-B-dominated,
definition-sensitive drift — but the *pooled* `init_primary` trend that was previously the headline
statistic (τ = +.27, p = .03) **no longer clears significance** under the corrected facilitator identity
(τ = +.20, p = .105). With "facilitator" now understood to be the same external advisor across both
teams, this trend is **not** direct evidence for P5 (leader-centric *consolidation*, which concerns a
team's *own* internal structure) regardless. At most it describes something adjacent, present mainly in
one team. **We do not cite this as support for P5.**

### T5 — Depth by initiator type (**the uncorrected "team A" finding does not replicate under the correction**)
With the corrected facilitator identity, facilitator-initiated events are **not** significantly
shallower than member-initiated ones in **either** team, under any definition: team A `init_primary`
Mann-Whitney p = .133 (was p = .007 in the uncorrected version); team A `init_floor` p = .228 (was
p = .010); team B was already null before (p = .27–.92) and remains null. Pooled at the meeting level,
`init_primary` paired Wilcoxon p = .457, `init_floor` p = .407, `init_question` p = .168 — none
significant. **The previously reported "facilitator-initiated events are shallower, but only in team A"
finding does not survive the identification correction and is withdrawn.** It was very likely an
artefact of 24/34 meetings' worth of team-member events being mislabeled "facilitator" under the old
constant-id rule, which mixed genuinely shallow facilitator-driven events with ordinary member events in
an inconsistent, meeting-dependent way.

## Sensitivity across the three initiator definitions (as required)
| test | init_primary | init_floor | init_question |
|---|---|---|---|
| Non-null coverage | 100% | 100% | 54% |
| Facilitator-initiated share (pooled) | 36.0% | 39.6% | 51.2% |
| Permutation test vs talk-time null | **p<.0001 (below null)** | **p=.004 (below null)** | **p=.002 (below null)** |
| Event class × initiator-type (χ², df=2) | p=.375 (n.s.) | p=.103 (n.s.) | p=.285 (n.s.) |
| Facilitator share vs week, pooled τ | +.20 (p=.105, n.s.) | **+.32 (p=.009)** | +.09 (p=.485, n.s.) |
| Facilitator share vs week, team A τ | −.13 (n.s.) | +.23 (n.s.) | −.31 (n.s.) |
| Facilitator share vs week, team B τ | **+.54 (p=.003)** | +.35 (p=.053) | +.30 (n.s.) |
| Depth: facilitator vs member (team A) | p=.133 (n.s.) | p=.228 (n.s.) | p=.098 (n.s.) |
| Depth: facilitator vs member (team B) | p=.267 (n.s.) | p=.185 (n.s.) | p=.772 (n.s.) |
| Stability H1 vs H2, team A ρ | .90 | .87 | .70 |
| Stability H1 vs H2, team B ρ | .20 | .20 | .70 |

**Where conclusions depend on the definition, this is stated plainly throughout.** After the
correction, the facilitator's below-null initiation share (T3) is the fully definition-invariant
result (significant in all three, all in the same direction); the longitudinal drift (T4) and depth
comparison (T5) remain team- and/or definition-dependent, with T5's prior team-A signal not surviving
the correction at all.

## Honest interpretation
- **The external facilitator initiates significantly *less* than their talk-time predicts** — the
  corrected, definition-invariant headline finding (it replaces the previous null "at chance" reading).
  This is consistent with the facilitator being a process-neutral outsider who talks a great deal
  (running the meeting) without disproportionately triggering the moments where the team's own
  communication pattern reorganizes.
- **The most consistently disproportionate initiator is the quietest team member**, not the facilitator
  — unaffected by the correction: rare interventions from low-talk-time members trigger reorganization
  more than their airtime would predict, in both teams, across two of three definitions. Read together
  with the corrected T3 result, the paper's bottom-up reading is, if anything, sharpened: both ends of
  the talk-time distribution point the same direction, away from proportional initiation by the most
  central/authoritative voice.
- **This study does not test P5.** P5 (leader-centric consolidation) is about a team's own internal
  leadership; the person identified and tracked here is an external advisor, likely the same individual
  across both teams. The weak, team-B-dominated, definition-fragile drift toward facilitator-initiation
  over time should **not** be reported as evidence for or against P5.
- **The class × initiator-type hypothesis is not supported**, before or after the correction.
- **The previously reported team-A depth asymmetry does not survive the correction and is withdrawn.**
  This is reported transparently as a correction, not silently dropped: the original number was an
  artefact of the identification bug, not a real effect.
- **n = 2 teams throughout, and both teams share the same facilitator** — every "pooled" statistic is
  dominated by whichever team happens to show the effect.
- **A true test of P3/P5 at the internal-leadership level remains open**: identifying each team's own
  internal leader (distinct from the shared external facilitator) is a natural follow-up this study does
  not attempt.

## Paper paragraph (drop-in, exact statistics, corrected)
> To move from floor *structure* to identifiable *persons* (P3, multiscale identity), we asked who
> initiates each of 909 reorganization events across 34 meetings, using three convergent definitions
> (first new speaker, floor-holder at onset, first questioner in the surrounding window; the latter
> covering 54% of events). The teams' external facilitator (identified per meeting from EOS L10
> segue/to-do-review patterns, verified against retained name-labeled source transcripts; the same
> advisor across both teams per this corpus's design) initiated reorganization **significantly less**
> than their talk-time predicts: a permutation test against a talk-time-weighted null found the
> facilitator's observed initiated-event share (36–51% across definitions) fell below the null in all
> three definitions (p < .0001, p = .004, p = .002). The most disproportionate initiator was, at the
> other extreme, each team's least-talkative member (initiation lift 1.9 and 1.4× their talk-time
> share) — the same asymmetry from both ends of the talk-time distribution. A weak, team-B-dominated
> drift of initiation toward the facilitator over time (pooled Kendall τ = +.20, n.s. for the primary
> definition; τ = +.32, p = .009 for the floor definition) was present mainly in one team (τ = +.54,
> p = .003) and vanished under the question-based definition; because the facilitator is external to
> the team, we do not interpret this as evidence for or against leader-centric consolidation (P5),
> which concerns a team's own internal leadership structure. The hypothesis that agenda-transition
> events are facilitator-driven while interior handoffs are member-driven was not supported
> (χ²(2) = 1.96–4.55, all p > .10).

## Honest scope
- 2 teams, **sharing the same external facilitator** — team-level heterogeneity dominates several
  results (T4); pooled statistics can mask a null-in-one-team pattern, and because the facilitator
  is constant, any "facilitator effect" difference between teams is really a difference in that team's
  relationship with the one advisor, not two facilitation styles.
- `init_question` covers only 54% of events (no question in window for the rest) — its weaker/absent
  effects may partly reflect this reduced, non-random subsample, not only a true absence of signal.
- The "dominant pre-window speaker" and "floor at onset" constructs use the same Last-Speaker-Holds /
  word-count conventions as the rest of this program, for consistency, but have not been validated
  against independent (e.g. human-coded) initiator judgments.
- Facilitator identification is now a per-meeting rule (corrected from a single constant), verified
  against retained, unpublished name-labeled transcripts — it remains a categorical rule, not a
  continuous measure, and identifies an external advisor, not either team's own internal leader.
  Identifying an internal leader is unattempted future work.
- **This correction (see `facilitator_identification.md`) changed three results materially**: T3
  reversed from null to a significant below-null finding; T4's pooled `init_primary` trend lost
  significance while `init_floor`'s gained it; T5's team-A depth asymmetry did not survive and is
  withdrawn. T2 (lift, stability, Gini) was unaffected.

## Deliverables
- `facilitator_identification.md` — documented, corrected facilitator-identification rule, numbers,
  and both terminology/method corrections.
- `data/facilitator_raw_id_verified.csv` — per-meeting facilitator raw `speaker_id`, verified against
  retained (unpublished) name-labeled transcripts; no names in this file.
- `src/build_events_initiators.py` → `data/events_initiators.csv` (909 events × 3 initiator definitions,
  event class, depth, pseudonymized speaker/facilitator labels; corrected facilitator flag).
- `src/descriptives.py` → `data/talk_time_share.csv`, `data/gini_by_team_definition.csv`,
  `data/initiation_lift.csv`, `data/stability_halves.csv`.
- `src/facilitator_tests.py` → `data/permutation_facilitator_share.csv`, `data/class_by_initiator_type.csv`.
- `src/longitudinal_and_depth.py` → `data/facilitator_share_vs_week.csv`, `data/depth_by_initiator_type.csv`.
- `src/fig_initiators.py` → `fig_initiators.{png,pdf,svg}` (regenerated with corrected data).
- All data numeric/pseudonymized; no verbatim transcript text and no names in any output.

## References
Wickman (2011, *Traction* / EOS Level 10 Meeting — facilitator role); this program's `METHODS.md`
("Each meeting pairs the team with the same advisor"); prior Studies 2, 5, 6, 7 of this program (event
definition, EOS stage extraction, consolidation trends, boundary/class logic).
