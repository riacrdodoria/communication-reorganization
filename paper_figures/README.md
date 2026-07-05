# Publication figure set — one figure per study

Paper-ready figures (one per study), generated at **600 dpi PNG + vector PDF + vector SVG** (text stays
crisp/selectable at any zoom). Shared house style in `paper_style.py`: coordination = teal (#2E7D8C),
deliberation/contrast = orange (#d95f02); each figure carries the headline finding, an in-panel statistics
box (test · statistic · p · n · significance), and a paper-ready caption. Significance: *p<.05, **p<.01,
***p<.001. Unit of inference = meeting (n = 34) unless noted.

Reproduce: `python fig_paper_S<k>.py` (needs `paper_style.py`; S1/S2/S4/S6 read metrics/transcripts).

## Captions

**Figure 1 — `fig_paper_S1_lsh_validation`.** Convergent-validity check for the Last-Speaker-Holds (LSH)
representation. (A) Within-meeting correlation between the %MaxEntropy trajectory on the standard
representation (silence kept as its own state) and on LSH (last floor-holder carried through gaps); the two
agree closely (entropy-trajectory median r ≈ .94; the reported .87–.93 spans all three metrics including
the noisier RMSE). (B) A representative meeting — the trajectories are visually near-identical. LSH is
adopted as a faithful, simpler substrate.

**Figure 2 — `fig_paper_S2_dynamics`.** What reorganization is, dynamically. (A) Pooled across all
meeting-seconds, entropy and %DET form one continuous manifold — not two discrete regimes (Sarle bimodality
coefficient = 0.18 < 0.555; the earlier bimodality was a %DET-saturation artefact removed by L_min = 8).
(B) The dispersion of pre→post entropy excursions at reorganization is ~2× and outside the 95% interval of
AR(1) and VAR(1) surrogates (200 each) — genuine structure beyond trivial oscillation. (C) Ascending and
descending limbs of the cycle are symmetric (median 51 vs 52 s; paired Wilcoxon p = .64, n.s.).

**Figure 3 — `fig_paper_S3_taxonomy_fingerprint`.** The content fingerprint of reorganization. Across all
six validated coding schemes, categories enriched when communication reorganizes are coordinative/
procedural (information-seeking, feedback, agreement, structuring; teal), while argumentation and
solution-construction are suppressed (orange). Bars = mean within-meeting density lift at reorganization
events (RMSE > mean + 2.33 SD) vs baseline; Wilcoxon signed-rank + BH-FDR; 28/40 categories significant.

**Figure 4 — `fig_paper_S4_floor_dynamics`.** Reorganization in conversational-floor terms (Edelsky F1↔F2).
Floor-concentration measures (top-speaker share, network/eigenvector centralization, Gini, influence
asymmetry, turn-length dispersion) correlate positively with %DET (high when stable = F1); floor breadth
rises as %DET falls. Reorganization is the floor equalizing and de-centralizing (F1→F2). Bars = mean
within-meeting r with %DET; Wilcoxon across meetings. Participation entropy* is the near-tautological
sanity check.

**Figure 5 — `fig_paper_S5_development`.** Over ~17 weekly meetings per team, dynamics (team-state
entropy ↓) and floor structure (network centralization ↑, leader eigenvector-centrality ↑, participation
entropy ↓) all move toward a fixed, leader-centric operating point with less moment-to-moment
reorganization — consolidation/routinization, replicated across both teams. Trends are Mann-Kendall
(Kendall τ), pooled and per team; dashed = OLS fit.

**Figure 6 — `fig_paper_S6_microstructure`.** (A) In ±30 s of a topic-episode boundary, team-state entropy
rises and %DET falls vs episode interiors — topic transitions are the naturalistic perturbation that drives
reorganization (non-circular: boundaries are lexical, metrics are turn-taking). (B) On the EOS Level 10
agenda these teams run, the procedural review stages reorganize more than the problem-solving (IDS) block —
reorganization is coordination, not deliberation. Paired Wilcoxon.

**Figure 7 — `fig_paper_S7_anatomy`.** Anatomy of a reorganization event: a redistribution of the speaking
floor. (A) ~1/3 is locked to topic/agenda transitions, ~2/3 is endogenous (handoffs/openings mid-topic).
(B) The trigger does not determine whether a reorganization occurs (equal RMSE prediction-error spike,
p = .44) but sets its depth (entropy/%DET differ, Kruskal–Wallis p < 1e-7). (C) Over 26 weeks the resting
baseline entropy falls (consolidation) while the above-baseline excursion is invariant — a stereotyped
event riding a sinking baseline.

**Figure 11 — `fig_paper_S11_replication_ledger`.** The two teams as an intensive longitudinal
replication design: every headline effect size from Studies 1–10 (n=148), normalized per-statistic
(divided by whichever team's estimate is larger in magnitude, sign preserved) and plotted Team A vs
Team B against the identity line, marker shape/color coding six statistic families. 88% pooled sign
agreement (114/130 across the four multi-category profile vectors alone); the four profile-vector
families — taxonomy fingerprint, floor measures, review-vs-IDS contrast, border-vs-interior contrast —
correlate between teams at Spearman r = 0.84–0.98 (all permutation p < .0001). Two flagged, non-hidden
non-replications (initiator-rank stability; facilitator-share longitudinal trend) sit off the diagonal.

**Figure 12 — `fig_paper_S12_socioemotional`.** The socioemotional signature of reorganization. (A)
Across an 8-category confirmatory family (Bales IPA positive/negative quadrants + act4teams-full
positive/negative facets), reorganization events show a one-sided positive signature: agreement,
positive socio-emotional acts, and solidarity rise significantly (BH-FDR q<.001–.0003, within-family);
no negative category survives FDR. (B) The positive signal is a sharp spike coincident with the event
itself (rises pre→onset, falls onset→post, both p<.02 by circular-shift null) — not a before-the-fact
lubricant nor an after-the-fact repair; the negative composite rises into the event but does not
recede afterward. Two attempted coding-free lexical markers (typed laughter, exclamation density)
returned null data in this ASR-transcribed corpus (documented, not plotted).
