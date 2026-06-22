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

### Anatomy of a reorganization — how much is topic transition, and what is the rest?
Reorganization events (seconds with rmse_g > mean + 2.33 SD) are decomposed by an attributable-fraction
split into a transition zone (±W s of a topic-episode start ∪ EOS Level 10 stage onset) vs the interior.
- **~⅓ transition, ~⅔ interior.** At W = 30 s, 32 % of events are transition-driven excess and 68 % are
  interior/background (W-sweep 20/80 → 43/57 at ±15/±45 s; events ≈ 2.7× denser inside zones). Topic
  boundaries carry almost all of the transition share. "Reorganization = topic transition" is real but
  partial — most of it is mid-topic.
- **The interior ⅔ is a floor phenomenon, not content.** Interior reorg vs interior baseline (per-meeting
  standardized difference, Wilcoxon, BH-FDR): speaker switches d = +1.06, active speakers +0.55,
  **top-speaker share −0.47**, network centralization −0.15 — the floor opens and de-concentrates; content
  measures move the *other* way (exploratory talk −0.37, semantic recurrence −0.43). The strongest
  predictors (switches/turns/speakers) are partly tautological with state-entropy; the non-tautological
  top-share/centralization and the independent content measures carry the interpretation.
- **Mechanism.** Among 475 interior events vs matched baselines: floor **handoff** (dominant holder
  changes) 60 % (1.7×), **round-robin** (≥3 speakers in quick sequence) 30 % (2.3×), **opening** 19 %
  (1.9×); 2.14 vs 1.54 distinct speakers in the peri-window. Questions are present (63 %) but pervasive
  (1.2×) — context, not cause.
- **Trigger sets depth, not existence.** The rmse prediction-error spike is statistically equal for
  transition vs interior-handoff events (p = .44), but topic transitions are *deeper* reorganizations
  (entropy 47.8 / %DET 63.4) than interior handoffs (45.0 / 68.9) than diffuse interior events
  (41.0 / 71.7); Kruskal–Wallis p < 1e-7 on entropy and %DET.
- **Form vs function (typology reliability).** Two independent annotators labelling 80 blind interior
  windows into a six-type interactional codebook agree at **Cohen's κ = 0.51** (moderate). Readers rarely
  see a *bare* handoff; they read the windows as collaborative acts — **QA/clarification 31 %,
  co-construction 27 %, decision/convergence 25 %** (consensus). The structural form (floor handoff/
  opening) and the read function (clarify/build/decide) are complementary layers.

**What the reorganization metric is pointing to:** a redistribution of the speaking floor — structurally a
handoff/opening (F1→F2), functionally the team's clarify/co-construct/decide moments. Topic shift triggers
~⅓ (and the deepest); the larger ⅔ is the team spontaneously pooling the floor.

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
| `reorg_decomposition.py` | transcripts + metrics + episode/L10 boundaries | `results/reorg_decomposition_union_W30.csv`, `results/reorg_interior_drivers.csv` | **yes** |
| `reorg_interior_mechanism.py` | transcripts + metrics + boundaries | `results/reorg_interior_mechanism.csv` | **yes** |
| `reorg_signature.py` | transcripts + metrics + boundaries | `results/reorg_signature.csv` | **yes** |
| `fig_reorg_decomp.py` | `results/reorg_*` | `figures/fig_reorg_decomp.png` | no |
| `reorg_anno_kappa.py` | `results/reorg_anno_{A,B,hidden}.json` | console (κ, typology) | no |

The interior-typology validation used two independent annotators on 80 blind windows; only their label
files (`results/reorg_anno_{A,B}.json`) and the id→(meeting, second, rule-label) map
(`results/reorg_anno_hidden.json`) are published. The annotated windows themselves carry verbatim
transcript text and are withheld with the transcripts.

## References
Edelsky (1981); Sacks, Schegloff & Jefferson (1974); Itakura (2001); Showers et al. (2015); Cotacallapa
et al. (2019); Sauer & Kauffeld (2013); Basu, Choudhury & Pentland (2001); Hung et al. (2008); Pangakis et
al. (2023, LLM-annotation validation). See `references.md`.
