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

## Method
A per-meeting panel of reorganization, floor, and content summaries (`longitudinal_poc.py` →
`results/longitudinal_panel.csv`; `longitudinal_taxonomy.py` →
`results/longitudinal_taxonomy_panel.csv`), with per-team Mann–Kendall trend tests; an interrupted
time-series / segmented regression around the gap (`interrupted_ts.py`); and a within-meeting capacity
analysis (`proposal_h.py` → `results/proposal_h_panel.csv`) using proxies robust to the sliding window
(dynamic range, event rate, episode duration).

## Results — three independent lenses converge on consolidation
- **Structure.** Mean entropy **declines** over 26 weeks in both teams (Kendall τ = −0.47*, −0.40*) and
  network centrality **rises** (+0.32, +0.41*): the floor consolidates / centralizes (toward F1).
- **Content.** Coordinative/procedural categories decline while exploratory reasoning and disagreement
  rise; the coordination−deliberation balance drifts toward **deliberation** (pooled pre-trend −0.092**).
- **Capacity.** The within-meeting dynamic range **contracts** (entropy range τ = −0.13, −0.41*): teams
  explore less of the F1↔F2 space as they mature.

Together: **maturation = consolidation / crystallization** — teams settle into a more fixed, deliberative,
leader-centric operating point (a routinization reading; Feldman & Pentland 2003). A Law-of-Requisite-
Variety hook (declining variety may reduce future adaptability) is noted as theory, not a tested claim.

The gap itself shows **no consistent structural effect** in the interrupted time-series (the level change
is opposite in sign across the two teams); a small, suggestive content "re-coordination" after the gap is
reported as exploratory only.

## Honest scope
Effects are modest (τ ≈ 0.13–0.47; few per-team p < .05); the strength is replication across two teams ×
three lenses. Entropy range and level co-decline and are partly mechanically linked (bounded metric), so
the range-contraction is not fully independent evidence.

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
