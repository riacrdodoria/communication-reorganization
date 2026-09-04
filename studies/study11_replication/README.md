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

**T1 — Ledger.** 27/28 comparable rows have both team estimates; **26/27 (96%) agree in direction**
(the taxonomy-fingerprint row is a placeholder pointing to the fuller T2 vector test). One row is
**explicitly flagged as a non-replication**, not smoothed over: the facilitator-initiation-share
longitudinal trend (Study 9: significant in Team B only, τ=+.54 p=.003, vs a small non-significant
*negative* τ=−.13 in Team A — a genuine sign disagreement). A second row, initiator-rank stability
(Study 9: ρ=.90 in Team A vs ρ=.20 in Team B), agrees in sign but is flagged for a large magnitude
difference. **A third facilitator-related statistic — whether the facilitator initiates more or less
than talk-time predicts — was corrected during review** (Study 9's original facilitator identification
used a constant raw id that was wrong in 24/34 meetings) and now **replicates strongly in both teams**:
the facilitator initiates significantly *less* than talk-time predicts (A p=.002, B p<.001), reversing
the earlier non-significant, sign-disagreeing result.

**T2 — Profile vectors (the strong test).** All four multi-category profiles replicate strongly:

| Family | n categories | Spearman r (A vs B) | permutation p | sign agreement |
|---|---|---|---|---|
| Taxonomy fingerprint (Study 3) | 40 | **0.969** | <1e-4 | 37/40 (92%) |
| Floor measures (Study 4) | 9 | **0.983** | <1e-3 | 9/9 (100%) |
| Review-vs-IDS content contrast (Study 6) | 41 | **0.840** | <1e-3 | 32/41 (78%) |
| Border-vs-interior content contrast (Study 7) | 40 | **0.844** | <1e-3 | 36/40 (90%) |
| **Pooled across all four** | 130 | — | — | **114/130 (88%), binomial p = 1.0e-19** |

**T3 — Longitudinal.** Of the 5 trends: 2 fully **REPLICATE** (both CIs exclude zero: mean-entropy
consolidation τ=−.47/−.40; baseline-entropy consolidation τ=−.47/−.43), 1 **PARTIALLY replicates**
(network centralization: same direction, only Team B's CI excludes zero), and 2 are same-direction but
**underpowered at n=17 meetings/team** (participation entropy; border-event excursion) — no trend
reverses sign.

## Honest interpretation
The program's central claim — a stable, content-general deliberation↔coordination axis along which
reorganization is organised — replicates as a *shape*, not merely a sign, across two independently
run teams: four entire multi-category profiles correlate at r = 0.84–0.98 between teams. This is
different from, and stronger than, simply noting that most individual numbers point the same way.
At the same time, two specific claims about the **facilitator's role over time** do not replicate
(rank stability, longitudinal drift toward facilitator-initiation) — and because the facilitator is an
external advisor shared across both teams (Study 9), this dissociation is read as informative, not as
noise: **the structural, content/floor-level architecture of reorganization is team-general; a
person-specific facilitation dynamic is not**, and the two should not be conflated when interpreting
this program's link to P5 (leader-centric consolidation). A third facilitator statistic — whether the
facilitator initiates disproportionately relative to talk-time — moves the other way after a Study 9
identification correction: it now replicates strongly (both teams significant, same direction),
sharpening rather than weakening the program's bottom-up reading (quietest members over-initiate,
facilitator under-initiates, in both teams).

## Honest scope
- n = 2 teams throughout — this is a replication design, not a generalization design (`METHODS.md` §6);
  T3's bootstrap CIs are appropriately wide at n=17 meetings/team and several trends are honestly reported
  as same-direction-but-underpowered rather than forced into a false REPLICATES/NON-REPLICATES binary.
- T2's permutation null shuffles category *labels* within each already-observed vector; it tests whether
  the specific pairing of categories (not just their marginal distribution) matches across teams, which
  is the correct null for a profile-shape claim.
- The 2 flagged non-replications are retained and reported exactly as data showed them, not adjusted, re-run
  with a friendlier method, or omitted.

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
