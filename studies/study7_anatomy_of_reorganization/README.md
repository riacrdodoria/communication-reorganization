# Study 7 — The anatomy of a reorganization event: trigger, floor mechanism, and content

## Rationale and gap
Studies 2–6 establish *that* communication reorganizes and *what axis* it lies on (coordination↔
deliberation; F1↔F2 floor). Study 6 showed topic boundaries are reorganization events — but how much of
all reorganization is that, and what is the rest? This study dissects a single event by **trigger,
interactional mechanism, and content**, unifying the content (S3), floor (S4) and transition (S6) accounts
at the event level.

## Method
Reorganization events = seconds with `rmse_g` above mean + 2.33 SD (per meeting). A **transition zone** =
±W s of any boundary (topic-episode start ∪ EOS Level 10 stage onset). Analyses: an attributable-fraction
split of events into transition vs interior; interior drivers (floor + content features); the interactional
mechanism of interior events vs matched baselines; trigger × metric magnitude; a two-annotator functional
typology; and a per-taxonomy border-vs-interior content lift. Statistics: per-meeting standardized
differences, Wilcoxon + BH-FDR, Kruskal–Wallis, Cohen's κ. (Stage/episode boundaries and the windows for
the interactional and content reads derive from the withheld transcripts; only numeric results, label
files, and figures are published.)

## Results
- **~⅓ transition, ~⅔ interior.** Attributable-fraction split (sums to 100 %): at W = 30 s, **32 %
  transition-driven excess, 68 % interior/background** (W-sweep 20/80 → 43/57 at ±15/±45 s; events ≈ 2.7×
  denser in zones). Topic boundaries carry nearly all the transition share. "Reorganization = topic
  transition" is real but partial.
- **The interior ⅔ is a floor phenomenon, not content.** Interior reorg vs baseline (per-meeting
  standardized diff, Wilcoxon, BH-FDR): speaker switches d = +1.06, active speakers +0.55, **top-speaker
  share −0.47**, network centralization −0.15; content moves the *other* way (exploratory −0.37, semantic
  recurrence −0.43). The switch/turn/speaker measures are partly tautological with state-entropy; the
  non-tautological top-share/centralization and the independent content measures carry the interpretation.
- **Mechanism (475 interior events vs matched baseline).** Floor **handoff** (dominant holder changes)
  60 % (1.7×), **round-robin** (≥3 speakers, quick sequence) 30 % (2.3×), **opening** 19 % (1.9×); 2.14 vs
  1.54 distinct speakers in the peri-window. Questions present (63 %) but pervasive (1.2×) — context, not
  cause.
- **Trigger sets depth, not existence.** The rmse peak is statistically equal for transition vs interior-
  handoff events (p = .44), but topic transitions are *deeper* (entropy 47.8 / %DET 63.4) than handoffs
  (45.0 / 68.9) than diffuse interior events (41.0 / 71.7); Kruskal–Wallis p < 1e-7 on entropy and %DET.
- **Form vs function (typology reliability).** Two independent annotators on 80 blind interior windows
  agree at **Cohen's κ = 0.51** (moderate). Readers rarely see a *bare* handoff; they read the windows as
  collaborative acts — **QA/clarification 31 %, co-construction 27 %, decision/convergence 25 %**
  (consensus). Structural form (handoff/opening) and read function (clarify/build/decide) are complementary
  layers.
- **Each taxonomy predicts BOTH perturbations the same way.** Per-category window-level lift at border vs
  interior peaks (Wilcoxon, BH-FDR): **border 25/40, interior 22/40** significant, every category the same
  direction — both perturbations are coordination (↑ non-arguable, asks-info, feedback, prop-question,
  agrees, structuring, cooperation; ↓ arguable, exploratory, gives-opinion, negotiation, testing,
  knowledge-transfer, names/links problem & solution). Two divergences: **border is deeper** (larger
  lifts), and a few **perturbation-specific** categories — border carries topic-change substance (names
  problem/solution, links solution, agreement, commissive), interior carries floor-handoff moves
  (directive, set-question, asks-opinion). `figures/fig_border_interior_taxonomy.png`.

- **The anatomy is developmentally invariant.** Over the ~26 weeks (Kendall τ, per team n = 17 + pooled),
  neither the *where* nor the *what* of reorganization drifts. Border-share trend pooled τ = −0.01
  (p = .95; 32.6 % → 32.2 % early→late). A per-meeting coordination−deliberation content composite —
  continuous (corr with rmse) and event-locked, overall and per taxonomy, at topic vs L10 borders
  separately — yields **0/11 pooled trends surviving BH-FDR** (q ≈ .98; content-axis 0.262 → 0.230). The
  only flickers are single-team and contradictory. Maturation (Study 5) modulates the *intensity/depth* of
  reorganization, not its anatomy. `figures/fig_reorg_longitudinal.png`,
  `figures/fig_reorg_taxonomy_longitudinal.png`.
- **What changes is the baseline, not the excursion.** Per meeting, per class, over weeks (Kendall τ,
  BH-FDR): the meeting **baseline entropy falls** (τ = −0.42, p < .005, both teams) and the absolute
  entropy at events falls with it (border −0.39, interior −0.33), but the **excursion above baseline** and
  the **spike prominence** are flat (border excursion τ = −0.16 n.s.; prominence +0.06 n.s.; early→late
  baseline 36.0 → 30.6 while the border excursion holds 14.6 → 13.9 and prominence 3.34 → 3.45). The
  reorganization is a **stereotyped excursion of fixed size riding on a baseline that consolidates
  downward** — three nested invariances (anatomy, content, excursion depth) plus one change (the resting
  operating point, = Study 5). `figures/fig_reorg_depth_longitudinal.png`.

## Interpretation
A reorganization event is a **redistribution of the speaking floor (F1→F2)** with two triggers — a topic/
agenda transition (~⅓, deeper, carrying the substance of changing topic) and an endogenous floor handoff
(~⅔, a baton-pass/opening in service of clarifying, co-constructing, or deciding). Content-wise both are
the same coordination event; the trigger sets depth and a thin content signature, not the kind of event.
The reorganization metric literally detects the floor reorganizing — sometimes because the topic changed,
mostly because the team reshuffles who holds it.

## Honest scope
Transition vs interior share is W-dependent (report the sweep). The strongest interior predictors are
partly tautological with the metric; the non-tautological floor and independent content measures carry the
claim. The functional typology κ = 0.51 is moderate and both annotators are LLMs — a human-coded subset is
required before publication (Pangakis et al. 2023). Window-level taxonomy (90 s) straddles boundaries:
appropriate for border events, coarse for the interior.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `reorg_decomposition.py` | transcripts + metrics + episode/L10 boundaries | `results/reorg_decomposition_union_W30.csv`, `results/reorg_interior_drivers.csv` | **yes** |
| `reorg_interior_mechanism.py` | transcripts + metrics + boundaries | `results/reorg_interior_mechanism.csv` | **yes** |
| `reorg_signature.py` | transcripts + metrics + boundaries | `results/reorg_signature.csv` | **yes** |
| `reorg_taxonomy_borderinterior.py` | transcripts + metrics + window codebooks + boundaries | `results/reorg_taxonomy_borderinterior.csv` | **yes** |
| `fig_reorg_decomp.py` | `results/reorg_*` | `figures/fig_reorg_decomp.png` | no |
| `fig_border_interior_taxonomy.py` | `results/reorg_taxonomy_borderinterior.csv` | `figures/fig_border_interior_taxonomy.png` | no |
| `reorg_anno_kappa.py` | `results/reorg_anno_{A,B,hidden}.json` | console (κ, typology) | no |
| `reorg_longitudinal.py` | metrics + boundaries | `results/reorg_longitudinal_panel.csv` | **yes** |
| `reorg_taxonomy_longitudinal.py` | metrics + window codebooks + boundaries | `results/reorg_taxonomy_longitudinal_panel.csv` | **yes** |
| `fig_reorg_longitudinal.py` | `results/reorg_longitudinal_panel.csv` | `figures/fig_reorg_longitudinal.png` | no |
| `fig_reorg_taxonomy_longitudinal.py` | `results/reorg_taxonomy_longitudinal_panel.csv` | `figures/fig_reorg_taxonomy_longitudinal.png` | no |
| `reorg_depth_longitudinal.py` | metrics + boundaries | `results/reorg_depth_longitudinal_panel.csv` | **yes** |
| `fig_reorg_depth_longitudinal.py` | `results/reorg_depth_longitudinal_panel.csv` | `figures/fig_reorg_depth_longitudinal.png` | no |

The interior-typology validation used two independent annotators on 80 blind windows; only their label
files (`results/reorg_anno_{A,B}.json`) and the id→(meeting, second, rule-label) map
(`results/reorg_anno_hidden.json`) are published. The annotated windows themselves carry verbatim
transcript text and are withheld with the transcripts.

## References
Gorman & Grimm et al. (2017); Edelsky (1981); Hearst (1997); Marks, Mathieu & Zaccaro (2001); Wickman
(2011, EOS Level 10); Pangakis et al. (2023, LLM-annotation validation). See `references.md`.
