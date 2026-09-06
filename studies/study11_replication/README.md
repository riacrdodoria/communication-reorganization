# Study 11 — The two teams as an intensive longitudinal replication design

## Rationale and gap
Every study in this program (1–10) reports results for Team A and Team B separately and treats
direction-consistency across them as the evidence standard (`METHODS.md` §6), rather than pooling for
statistical power. That practice has been implicit. This study makes it explicit and formal: it treats
the n = 2 teams × 34 meetings corpus as an **intensive longitudinal replication design** (Bolger &
Laurenceau, 2013; Molenaar, 2004) — each team is a full, independently-measured replication of the same
process, not a "subject" in an n=2 statistical sample — and audits, in one place, how well every
headline effect size from Studies 1–10 actually replicates when the two teams' numbers are placed
side by side. This is the single most direct test of whether this program's central thesis
(reorganization = coordination, not deliberation, organised along a stable deliberation↔coordination
axis) is a property of *communication dynamics in general* or an artifact of one team's idiosyncrasies.

## Method
Three tasks, run against the corpus and the existing study outputs (never a new metric):

**T1 — Replication ledger.** 28 headline statistics spanning Studies 1–10 (LSH validity, bimodality
coefficient, supra-autoregressive excursion ratio, taxonomy-fingerprint sign agreement, 9 floor
measures, topic-boundary Δentropy/Δ%DET, review-vs-IDS Δentropy/Δreorg-rate, transition-share, 5
longitudinal Kendall taus, 4 Study 9 initiator statistics, 1 Study 8 outcome null), each recomputed
independently for Team A and Team B using the **exact method and parameters of the original study**
(never a new metric) and compared for same-direction agreement, joint significance, and a magnitude
ratio (min/max of |A|,|B|).

**T2 — Profile-vector replication (the strong test).** Single-number direction agreement is a weak
standard when many of the 28 statistics are correlated. The decisive test is whether the *entire
multi-category profile* replicates as a shape, not just its sign: for each of four families —
(a) the 40-category taxonomy-fingerprint lift vector (Study 3), (b) the 9-measure floor vector (Study
4), (c) the 41-category review-vs-IDS content-contrast vector (Study 6), (d) the 40-category
border-vs-interior content-contrast vector (Study 7) — the Team A and Team B vectors are correlated
(Spearman r) against a permutation null (shuffle category labels, 10,000 seeded draws), plus a
sign-agreement binomial test on the same vectors.

**T3 — Longitudinal replication with bootstrap CIs.** The 5 longitudinal Kendall taus (Study 5: mean
entropy, network centralization, participation entropy; Study 7: baseline entropy, border-event
excursion) are each given a meeting-clustered bootstrap 95% CI (resample meetings with replacement
**within team**, recompute tau, 2000 reps), and classified as REPLICATES (same direction, both CIs
exclude zero), PARTIAL (same direction, one CI excludes zero), SAME-DIRECTION-UNDERPOWERED (same
direction, neither CI excludes zero), or NON-REPLICATION (opposite direction).

## Results

**T1 — Ledger (rebuilt 2026-09-05 on the corrected corpus and person-level roles).** 27/28 comparable
rows have both team estimates; **26/27 (96%) agree in direction** (the taxonomy-fingerprint row is a
placeholder pointing to the fuller T2 vector test). One row is **flagged as a non-replication**: the
facilitator-initiation-share longitudinal trend (Study 9: Team B τ = +.52, p = .004; Team A τ = −.08,
p = .65). Two rows that an earlier version flagged — initiator-rank stability (ρ = .90 vs .20) and the
quiet-member lift — were artefacts of per-meeting speaker labels; on verified persons they replicate
(stability ρ = .80 / .90; least-talkative member lift 1.38 / 1.29). The facilitator's initiation share
replicates in both teams (below its talk-time null, A p = .01, B p < .002). Rows that depend on absolute
entropy (bimodality coefficient, the longitudinal taus, baseline entropy) changed value with the corpus
correction; rows built on within-meeting contrasts, ranks, %DET or event rates did not.

**T2 — Profile vectors (the strong test).** All four multi-category profiles replicate strongly:

| Family | n categories | Spearman r (A vs B) | permutation p | sign agreement |
|---|---|---|---|---|
| Taxonomy fingerprint (Study 3) | 40 | **0.965** | 1e-4 (0/10,000) | 38/40 (95%) |
| Floor measures (Study 4) | 9 | **0.967** | < 1e-4 | 9/9 (100%) |
| Review-vs-IDS content contrast (Study 6) | 41 | **0.840** | < 1e-4 | 32/41 (78%) |
| Border-vs-interior content contrast (Study 7) | 40 | **0.856** | < 1e-4 | 36/40 (90%) |
| **Pooled across all four** | 130 | — | — | **115/130 (88%)** (descriptive; the 130 items are not independent, so the binomial p is not reported) |

**T3 — Longitudinal (corrected).** Of the 5 trends, **1 partially replicates** (network centralization:
τ = +.07 / +.38, only Team B's CI excludes zero) and 4 are same-direction with both CIs including zero:
mean entropy τ = −.09 / −.16, participation entropy −.38 / −.29, baseline entropy −.09 / −.19, border
excursion +.12 / +.25. An earlier version reported two full replications (mean-entropy and
baseline-entropy "consolidation", τ ≈ −.4 to −.5 in both teams); both were produced by the
transcription-tool line that deflated entropy in the ten latest meetings of both teams (`METHODS.md`
§1, §8) and do not exist in the cleaned corpus. The bootstrap seeds are now deterministic, so every
interval in `results/longitudinal_bootstrap.csv` regenerates exactly.

## Honest interpretation
The program's central claim — a stable, content-general deliberation↔coordination axis along which
reorganization is organised — replicates as a *shape*, not merely a sign, across two independently
run teams: four entire multi-category profiles correlate at r = 0.84–0.98 between teams. This is
different from, and stronger than, simply noting that most individual numbers point the same way.
At the same time, the one claim about the **facilitator's role over time** (a drift toward
facilitator-initiation) holds in one team only — and because the facilitator is an external advisor
shared across both teams (Study 9), this is read as informative, not as noise: **the structural,
content/floor-level architecture of reorganization is team-general; a person-specific facilitation
dynamic is not**. The person-level statistics that do replicate (facilitator under-initiates floor-taking
events, least-talkative member over-initiates, initiator ranks stable) support the program's bottom-up
reading in both teams. What does *not* replicate — because it does not exist once the corpus is
corrected — is developmental consolidation of the resting entropy: the corpus offers no evidence that
the teams' turn-taking baseline drifts over six months.

## Honest scope
- n = 2 teams throughout — this is a replication design, not a generalization design (`METHODS.md` §6);
  T3's bootstrap CIs are appropriately wide at n=17 meetings/team and several trends are honestly reported
  as same-direction-but-underpowered rather than forced into a false REPLICATES/NON-REPLICATES binary.
- T2's permutation null shuffles category *labels* within each already-observed vector; it tests whether
  the specific pairing of categories (not just their marginal distribution) matches across teams, which
  is the correct null for a profile-shape claim.
- The flagged non-replication is retained and reported exactly as the data show it. The label-shuffle
  permutation in T2 tests whether the *pairing* of categories matches across teams; it does not test
  whether between-team similarity exceeds within-team (split-half) similarity, which is not attempted.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `src/team_utils.py` | — | shared `team_of()` helper | no |
| `src/build_ledger.py` | transcripts + metrics (LSH validity, BC, supra-AR) | `results/replication_ledger_part1.csv` | **yes** |
| `src/build_ledger_part2.py` | Studies 1-9 result CSVs + part1 | `results/replication_ledger.csv`, `results/taxonomy_lift_by_team.csv` | no |
| `src/profile_replication.py` | `results/taxonomy_lift_by_team.csv`, ledger, episode/L10/codebook data | `results/review_vs_ids_by_team.csv`, `results/border_interior_by_team.csv`, `results/profile_replication_summary.csv`, `results/profile_sign_agreement_overall.csv` | **yes** (for the two fresh per-team content contrasts) |
| `src/longitudinal_bootstrap.py` | `longitudinal_panel.csv`, `reorg_depth_longitudinal_panel.csv` | `results/longitudinal_bootstrap.csv` | no |
| `../../paper_figures/fig_paper_S11.py` | all of the above | `../../paper_figures/fig_paper_S11_replication_ledger.{png,pdf,svg}` | no |

All published outputs are numeric only.

## References
Bolger & Laurenceau (2013); Molenaar (2004); Benjamini & Hochberg (1995); this program's Studies 1–10
(every headline statistic re-tested here). See `references.md`.
