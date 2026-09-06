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
  centralization and top eigenvector-centrality ↓, dyadic transition asymmetry ↓. (Network measures
  corrected 2026-09-05, `src/floor_measures.py`: Freeman centralization normalised to [0,1] so it is not
  mechanically tied to the number of active speakers; principal eigenvector by eigendecomposition
  instead of a non-converging power iteration; the earlier in–out asymmetry, which for a single
  transition sequence reduces to ≈ 1/n_transitions, replaced by the share of non-reciprocated dyadic
  transitions. Directions and significance of all nine measures are unchanged.)
- **Event-locked confirmation.** Snapshots in ±45 s of entropy peaks vs valleys show, on the non-
  tautological structure measures (top-speaker share, network centralization, dyadic asymmetry), the same
  F2-at-peak / F1-at-valley pattern — confirming it is floor *structure*, not just participation counts,
  that reorganizes.
- **Scale.** Network-centrality effects strengthen on longer windows and per meeting (e.g. per-meeting
  network centralization vs mean entropy r ≈ −0.86).
- **Static vs dynamic.** Floor *centrality* (who is central) predicts a meeting's overall reorganization
  level (between-meeting); influence *directionality* (who drives the next turn; Influence Model) shifts
  moment-to-moment within a meeting but is not a between-meeting trait.

### Anatomy at the event level → Study 7
Because the floor account *is* the reorganization, the metrics let us dissect a single event by trigger,
mechanism and content. That grew into its own study — see
[`studies/study7_anatomy_of_reorganization`](../study7_anatomy_of_reorganization). Headline: a
reorganization is a redistribution of the speaking floor (F1→F2); **~⅓ topic/agenda transition (deeper) +
~⅔ endogenous floor handoff/opening** (function: clarify / co-construct / decide); the trigger grades the
event (TRANSITION > HANDOFF > OTHER on all three metrics); and each taxonomy predicts both perturbations
the same way (both coordination).

## Honest scope
Participation entropy ≈ the Gorman entropy (r ≈ .81) and is a sanity check, not independent evidence; the
independent crosses are top-speaker share, dyadic transition asymmetry, and the F1/F2 index. Network measures need
≥ 300 s windows to be reliable. Interruptions, overlaps, and precise floor-transfer offsets require
audio and are noted as future work.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `triangulation_floor.py` | transcripts + metrics | `results/floor_windows.csv` | **yes** |
| `fig_floor.py` | `results/floor_windows.csv` | `figures/fig_floor.png` | no |
| `floor_network_window.py` | transcripts + metrics | `results/floor_network_meeting.csv` | **yes** |
| `influence_model.py` | transcripts + metrics | `results/influence_meeting.csv` | **yes** |

(The event-level anatomy scripts now live in
[`studies/study7_anatomy_of_reorganization`](../study7_anatomy_of_reorganization).)

## References
Edelsky (1981); Sacks, Schegloff & Jefferson (1974); Itakura (2001); Showers et al. (2015); Cotacallapa
et al. (2019); Sauer & Kauffeld (2013); Basu, Choudhury & Pentland (2001); Hung et al. (2008). See
`references.md`.
