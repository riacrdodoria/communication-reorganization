# Study 4 — Reorganization as conversational-floor dynamics

## Rationale and gap
The reorganization metrics are, in fact, floor metrics: entropy of the speaker state is a participation-
distribution entropy, and %DET measures the predictability of the floor-holding sequence. Yet the
conversation-floor / participation / centrality literature and the entropy / recurrence literature have
never been related to each other. This study names the deliberation↔coordination axis in established
floor terms — **Edelsky's singly-developed (F1) vs collaborative (F2) floor** — and makes that
previously-unmade cross.

## Method
Nine coding-free floor / turn-taking / centrality measures per 90 s window (`triangulation_floor.py` →
`results/floor_windows.csv`): participation Gini and entropy, top-speaker share, an F1/F2 index
(dispersion of turn length across speakers), active-speaker count, turn-transition-network degree
centralization and eigenvector centrality, and an in–out asymmetry index (a windowed proxy for who drives
floor transitions). Each is cross-referenced with entropy/%DET/RMSE (Stouffer Z, within-meeting circular
null). Network measures are additionally recomputed on longer windows and per meeting
(`floor_network_window.py`), and the Influence Model (Basu, Choudhury & Pentland) is fit per meeting
(`influence_model.py`).

## Results
- **All nine measures track reorganization coherently.** At reorganization the floor **equalizes and
  de-centralizes**: top-speaker share ↓ (r ≈ .52 vs %DET), participation Gini ↓, participation entropy ↑,
  turn-length dispersion ↓ (Edelsky's "neutralization" of F2), more active speakers, network
  centralization and top eigenvector-centrality ↓, in–out asymmetry ↓.
- **Event-locked confirmation.** Snapshots in ±45 s of entropy peaks vs valleys show, on the non-
  tautological structure measures (top-speaker share, network centralization, in–out asymmetry), the same
  F2-at-peak / F1-at-valley pattern — confirming it is floor *structure*, not just participation counts,
  that reorganizes.
- **Scale.** Network-centrality effects strengthen on longer windows and per meeting (e.g. per-meeting
  network centralization vs mean entropy r ≈ −0.86).
- **Static vs dynamic.** Floor *centrality* (who is central) predicts a meeting's overall reorganization
  level (between-meeting); influence *directionality* (who drives the next turn; Influence Model) shifts
  moment-to-moment within a meeting but is not a between-meeting trait.

## Honest scope
Participation entropy ≈ the Gorman entropy (r ≈ .81) and is a sanity check, not independent evidence; the
independent crosses are top-speaker share, in–out asymmetry, and the F1/F2 index. Network measures need
≥ 300 s windows to be reliable. Interruptions, overlaps, and precise floor-transfer offsets require
audio and are noted as future work.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `triangulation_floor.py` | transcripts + metrics | `results/floor_windows.csv` | **yes** |
| `fig_floor.py` | `results/floor_windows.csv` | `figures/fig_floor.png` | no |
| `floor_network_window.py` | transcripts + metrics | `results/floor_network_meeting.csv` | **yes** |
| `influence_model.py` | transcripts + metrics | `results/influence_meeting.csv` | **yes** |

## References
Edelsky (1981); Sacks, Schegloff & Jefferson (1974); Itakura (2001); Showers et al. (2015); Cotacallapa
et al. (2019); Sauer & Kauffeld (2013); Basu, Choudhury & Pentland (2001); Hung et al. (2008). See
`references.md`.
