# Study 5 — Developmental trajectories

## Rationale and gap
The corpus is an **intensive longitudinal panel**: two teams, 17 weekly meetings each, over ~26 weeks.
Naturalistic, fine-grained, multi-month communication-reorganization is rare; this study asks how
reorganization *develops* as a team matures, answering standing calls for in-the-wild, longitudinal
team-dynamics data.

## Design and honest framing
With **n = 2 teams** there is no between-team statistical generalisation. The study is framed as a
comparative intensive-longitudinal design in which the two teams provide **replication / direction-
consistency**, not statistical power; single p-values are secondary to whether the two teams agree in
direction. The series carry one long mid-January→February gap (a real ~4–6 week summer break, confirmed
in the source recordings), which is described as such and not interpreted as a perturbation.

## Correction (2026-09-05) — read this first
An earlier version of this study reported that **mean entropy declines** over the 26 weeks in both teams
(τ = −0.47 / −0.40) and read this, together with Study 7, as *consolidation of the resting operating
point*. That result was an artefact. From 17 March 2025 the transcription tool inserted one automatic
announcement line at the start of each recording; in the ten affected meetings — the last five weeks of
**both** teams — that line was carried as an extra anonymous speaker, so the entropy normaliser
(%MaxEnt = H / n_speakers) was inflated by one and entropy was deflated by 20–25 % exactly in the late
meetings. With the line removed (`METHODS.md` §1) the entropy trend is null (τ = −0.09 / −0.16). All
numbers below are from the corrected corpus; the earlier consolidation reading is withdrawn.

## Method
A per-meeting panel of reorganization, floor, and content summaries (`longitudinal_poc.py` →
`results/longitudinal_panel.csv`; `longitudinal_taxonomy.py` →
`results/longitudinal_taxonomy_panel.csv`), with per-team Mann–Kendall trend tests; an interrupted
time-series / segmented regression around the gap (`interrupted_ts.py`); and a within-meeting capacity
analysis (`proposal_h.py` → `results/proposal_h_panel.csv`) using proxies robust to the sliding window
(dynamic range, event rate, episode duration).

## Results — what develops, and what does not
- **Structure.** Mean entropy: τ = −0.09 (A), −0.16 (B), both n.s. Mean %DET: +0.19, +0.15, n.s.
  Reorganization-event rate: −0.37* (A), +0.13 (B) — opposite directions. **Network centralization
  rises** in both teams (+0.32, +0.43*; the only structural trend that replicates in direction with one
  team significant; Study 11 bootstrap: partial replication). Top-speaker share +0.26 / +0.25, n.s.
- **Content.** No single category trend survives BH-FDR (0/82 category × team tests). Five categories
  agree in direction with at least one team at p < .10 (asks-opinion ↓, structuring ↓, convergence ↓,
  non-arguable ↓, exploratory ↑). The coordination−deliberation balance composite drifts weakly toward
  deliberation in both teams (τ = −0.13, −0.26), not significantly.
- **Capacity.** Entropy range τ = +0.21 (A), −0.03 (B); %DET range −0.13, −0.31; valley depth +0.07,
  +0.34; episode duration −0.15, +0.10. No capacity proxy replicates in direction with a significant team.

Together: over 26 weeks the teams' turn-taking **does not consolidate**. The resting entropy, the %DET
level and the size of reorganization excursions (Study 7) are developmentally flat; the one replicated
drift is a mild centralization of the transition network. The Law-of-Requisite-Variety hook and the
routinization reading offered earlier are no longer supported by these data and are dropped.

The gap shows **no consistent structural effect** in the interrupted time-series (entropy level change
−10.0 in Team A vs +6.7 in Team B; pooled −1.2).

## Honest scope
Effects are small (|τ| ≤ 0.43; one per-team p < .05 per lens); with 17 meetings per team the bootstrap
intervals (Study 11) include zero for every trend except Team B's centralization. The earlier trend was
produced by a data defect that was invisible in the anonymised metrics and only surfaced when the
name-labelled source transcripts were re-inspected; the metrics in `data/metrics_gorman_l8/` are now the
cleaned series.

## Scripts
| script | reads | writes |
|---|---|---|
| `longitudinal_poc.py` | metrics + floor/triangulation tables | `results/longitudinal_panel.csv`, `figures/fig_longitudinal.png` |
| `longitudinal_taxonomy.py` | taxonomy counts | `results/longitudinal_taxonomy_panel.csv`, `figures/fig_longitudinal_taxonomy.png` |
| `interrupted_ts.py` | the two panels | console |
| `proposal_h.py` | metrics | `results/proposal_h_panel.csv`, `figures/fig_proposal_h.png` |

## References
Kozlowski (2015); Cronin, Weingart & Todorova (2011); Klonek et al. (2019); Marks, Mathieu & Zaccaro
(2001); Gersick (1991); Ancona & Chong (1996); Feldman & Pentland (2003); Bolger & Laurenceau (2013);
Wagner et al. (2002). See `references.md`.
