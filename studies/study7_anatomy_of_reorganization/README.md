# Study 7 — The anatomy of a reorganization event: trigger, floor mechanism, and content

## Rationale and gap
Studies 2–6 establish *that* communication reorganizes and *what axis* it lies on (coordination↔
deliberation; F1↔F2 floor). Study 6 showed topic boundaries are reorganization events — but how much of
all reorganization is that, and what is the rest? This study dissects a single event by **trigger,
interactional mechanism, and content**, unifying the content (S3), floor (S4) and transition (S6) accounts
at the event level.

## Method
Reorganization events = seconds with `rmse_g` above mean + 2.33 SD (per meeting), clustered at 8 s gaps; the
trigger classes (TRANSITION / INTERIOR_HANDOFF / INTERIOR_OTHER) come from the single shared implementation
`src/reorg_events.py` (centre within ±30 s of a boundary; dominant floor-holder by turn count in the 30 s
before vs after; see `METHODS.md` §4 and `results/reorg_class_sensitivity.csv` for the rule sensitivity).
A **transition zone** = ±W s of any boundary (topic-episode start ∪ EOS Level 10 stage onset). Analyses: an attributable-fraction
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
  standardized diff, Wilcoxon, BH-FDR): speaker switches d = +1.06, active speakers +0.53, **top-speaker
  share −0.45**, network centralization −0.15 (n.s.); content moves the *other* way (exploratory −0.37;
  semantic recurrence −0.43, but see Study 3: semantic recurrence is itself a turn-length proxy). The switch/turn/speaker measures are partly tautological with state-entropy; the
  non-tautological top-share/centralization and the independent content measures carry the interpretation.
- **Mechanism (480 interior events vs matched baseline).** Floor **handoff** (dominant holder changes)
  58 % (1.7×), **round-robin** (≥3 speakers, quick sequence) 30 % (2.4×), **opening** 18 % (1.9×); 2.13 vs
  1.55 distinct speakers in the peri-window. Questions present (62 %) but pervasive (1.2×) — context, not
  cause. (This script drops zone seconds before clustering, so its interior count, 480, differs from the
  445 interior events of the cluster-then-classify rule used everywhere else; the annotated typology
  sample was drawn from the former.)
- **Trigger grades the event.** With the meeting as the unit (per-meeting class means, n = 34; `results/`
  `reorg_signature_meeting_level.csv`), topic transitions are larger than interior handoffs on **all three**
  metrics: rmse peak +0.20 SD (higher in 24/34 meetings, paired Wilcoxon p = .004), entropy +0.17 SD
  (21/34, p = .04), %DET −0.31 SD (p = .0002); Friedman across the three classes p ≤ .001 on each. Raw
  means: entropy 50.9 / 48.4 / 44.2 and %DET 63.3 / 68.8 / 71.4 for TRANSITION / HANDOFF / OTHER;
  Kruskal–Wallis on within-meeting z p < 1e-7. An earlier event-level test had read the rmse contrast as
  null (p = .44); at the meeting level it is not. The honest statement is a graded ordering
  TRANSITION > HANDOFF > OTHER, with the rmse difference smaller than the %DET difference.
- **Form vs function (typology reliability).** Two independent annotators on 80 blind interior windows
  agree at **Cohen's κ = 0.51** (moderate). Readers rarely see a *bare* handoff; they read the windows as
  collaborative acts — **QA/clarification 31 %, co-construction 27 %, decision/convergence 25 %**
  (consensus). Structural form (handoff/opening) and read function (clarify/build/decide) are complementary
  layers.
- **Each taxonomy predicts BOTH perturbations the same way.** Per-category window-level lift at border vs
  interior peaks (Wilcoxon, BH-FDR): **border 25/40, interior 22/40** significant, 37/40 categories in the
  same direction — both perturbations are coordination (↑ non-arguable, asks-info, feedback, prop-question,
  agrees, structuring, cooperation; ↓ arguable, exploratory, gives-opinion, negotiation, testing,
  knowledge-transfer, names/links problem & solution). Two divergences: **border is deeper** (larger
  lifts), and a few **perturbation-specific** categories — border carries topic-change substance (names
  problem/solution, links solution, agreement, commissive), interior carries floor-handoff moves
  (directive, set-question, asks-opinion). `figures/fig_border_interior_taxonomy.png`.

- **The anatomy is developmentally invariant.** Over the ~26 weeks (Kendall τ, per team n = 17 + pooled),
  neither the *where* nor the *what* of reorganization drifts. Border-share trend pooled τ = −0.02
  (p = .86; 32.6 % → 31.5 % early→late). A per-meeting coordination−deliberation content composite —
  continuous (corr with rmse) and event-locked, overall and per taxonomy, at topic vs L10 borders
  separately — yields **0/11 pooled trends surviving BH-FDR** (q ≈ .98; content-axis 0.262 → 0.230). The
  only flickers are single-team and contradictory (Team A's interior rate τ = −0.37, p = .04; Team B
  +0.19). `figures/fig_reorg_longitudinal.png`,
  `figures/fig_reorg_taxonomy_longitudinal.png`.
- **Neither the baseline nor the excursion drifts (corrected 2026-09-05).** Per meeting, per class, over
  weeks (Kendall τ, BH-FDR over 10 measures): **0/10 trends survive**. Baseline entropy τ = −0.16 (p = .18;
  early→late 36.1 → 34.5), entropy at border events −0.03, border excursion +0.13 (14.6 → 15.8), spike
  prominence +0.03 (3.34 → 3.47), %DET excursion −0.05. An earlier version reported a falling baseline
  (τ = −0.42) with a fixed excursion ("three invariances + one change"); the fall was produced by the
  transcription-tool line that deflated entropy in the ten latest meetings (`METHODS.md` §1, §8). The
  reorganization is a **stereotyped excursion of fixed size on a resting point that does not drift** —
  anatomy, content, depth and baseline are all developmentally invariant in this corpus.
  `figures/fig_reorg_depth_longitudinal.png`.

## Interpretation
A reorganization event is a **redistribution of the speaking floor (F1→F2)** with two triggers — a topic/
agenda transition (~⅓, deeper, carrying the substance of changing topic) and an endogenous floor handoff
(~⅔, a baton-pass/opening in service of clarifying, co-constructing, or deciding). Content-wise both are
the same coordination event; the trigger sets depth and a thin content signature, not the kind of event.
The reorganization metric literally detects the floor reorganizing — sometimes because the topic changed,
mostly because the team reshuffles who holds it. Over six months none of this changes.

## Honest scope
Transition vs interior share is W-dependent (report the sweep). The handoff/other split among interior
events is rule-dependent (195–275 handoffs across five reasonable rules, 57–78 % agreement with the
canonical rule; `results/reorg_class_sensitivity.csv`); the TRANSITION class and every conclusion that
pools the interior classes are not affected. The consensus typology percentages are computed on the 48/80
items the two annotators agreed on, and the annotators differ markedly in their use of OTHER (27/80 vs
5/80); the full marginals are in the label files. The strongest interior predictors are
partly tautological with the metric; the non-tautological floor and independent content measures carry the
claim. The functional typology κ = 0.51 is moderate and both annotators are LLMs — a human-coded subset is
required before publication (Pangakis et al. 2023). Window-level taxonomy (90 s) straddles boundaries:
appropriate for border events, coarse for the interior.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `reorg_decomposition.py` | transcripts + metrics + episode/L10 boundaries | `results/reorg_decomposition_union_W30.csv`, `results/reorg_interior_drivers.csv` | **yes** |
| `reorg_interior_mechanism.py` | transcripts + metrics + boundaries | `results/reorg_interior_mechanism.csv` | **yes** |
| `reorg_signature.py` | transcripts + metrics + boundaries | `results/reorg_signature.csv`, `results/reorg_signature_meeting_level.csv` | **yes** |
| `reorg_class_sensitivity.py` | transcripts + metrics + boundaries | `results/reorg_class_sensitivity.csv` | **yes** |
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
