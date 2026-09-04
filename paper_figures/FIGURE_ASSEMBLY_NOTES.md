# Figure assembly notes — Phase 1 composite figures

Three composite figures assembled per the SGR-paper storyboard brief, plus the existing S11
replication-ledger figure serving as the supplementary figure (no new work needed there).

## Method note (read this first)
The storyboard's guardrail said "extract only the needed panel(s) using matplotlib or PIL/pypdf —
do NOT crop manually." All of this program's `fig_paper_S*.py` scripts draw multiple panels together
in one in-memory matplotlib figure (via `plt.subplots`/`GridSpec`) and only the assembled PNG/PDF is
saved — there is no per-panel intermediate file to crop, and pixel-cropping a 600dpi PNG at precise,
non-arbitrary panel boundaries is exactly the kind of fragile, eyeballed operation the guardrail is
warning against. Since every source figure's data and plotting logic is available and reproducible
(nothing in this program depends on unrecoverable manual annotation), each composite panel below was
built by **re-deriving the exact same statistic from the exact same data source** the original study
figure uses, then redrawing it at the composite's required size. This is "extraction using
matplotlib" in the sense the guardrail intends (precise, scripted, reproducible — not manual), while
avoiding the resolution/margin mismatches that pixel-cropping across differently-sized source figures
would introduce. **No `fig_paper_S*.py` source script was modified**; all three composite scripts
(`fig1_computational_structure.py`, `fig2_multilevel_structure.py`, `fig3_temporal_structure.py`) are
new, standalone files.

## Decisions confirmed with the user before building (per the briefing's "do not guess" list)
1. **Fig 1 Panel B**: include the L_min=2-vs-L_min=8 saturation inset (user chose this over the
   "unimodality alone" default). Implemented as a small "% of windows ≥95% DET" bar comparison
   (92% at L_min=2 vs 28% at L_min=8) rather than overlapping histograms, which were unreadable at
   the required inset size — a clearer encoding of the same underlying artefact.
2. **Fig 2 Panel A**: full 40-category fingerprint (`fig_paper_S3`/`peaks_taxonomy_sig.csv`), not the
   by-taxonomy breakdown. Note: `fig_reorg_taxonomy_bytax.png` (the alternative) exists only as a flat
   raster in `~/lsh-work` with no corresponding source script — it could not have been cleanly
   extracted/regenerated without reverse-engineering its binning from scratch, which reinforced the
   recommendation independently of the persuasiveness argument.
3. **Fig 3 Panel C**: Study 7's baseline-vs-excursion panel (`reorg_depth_longitudinal_panel.csv`),
   not Study 5's broader consolidation panel — it isolates the "sinking baseline, stable peaks"
   dissociation the panel is meant to show.

## Figure 1 — Computational structure (3 panels, reused: 2, new: 1)
- **A (Substrate validity)**: reused Study 1's per-meeting LSH-vs-standard correlation logic
  (`fig_paper_S1.py`'s Panel A) exactly — median r=.94, all meetings ≥.90.
- **B (Continuum, not two regimes)**: **new panel**. The storyboard asked for a 1-D entropy
  histogram + Gaussian overlay + BC, which is not what Study 2's existing panel shows (that panel is
  a 2-D entropy×%DET hexbin geometry plot). Built fresh from `data/metrics_gorman_l8/*_gorman.csv`
  (already-cached, no transcript access needed). The L_min inset **is** a genuine workaround: %DET at
  L_min=2 is not cached anywhere in this program's existing outputs (only the current L_min=8 %DET
  is), so a new script (`_cache_lmin_comparison.py`) recomputes both from the raw transcripts (15s
  runtime, reusing `gorman_reimpl.py`'s `det_window()` unmodified) and caches the result.
- **C (Excursion exceeds AR chance)**: reused Study 2's supra-AR surrogate bar panel exactly.
- **Legibility**: all three panels read cleanly at 7.0×2.8in; panel titles were shortened/wrapped to
  two lines to prevent adjacent-panel title collisions at this width — a real constraint of fitting
  3 panels in 7in that single-figure versions don't face.

## Figure 2 — Individual and team-level structure (4 panels, reused: 1, new: 3)
- **A (Content fingerprint)**: reused Study 3's 40-category lift data (`peaks_taxonomy_sig.csv`)
  directly, but the **rendering is a workaround**, not a straight reuse: Study 3's own figure is
  8.4×9.2in specifically because 40 individually-labeled rows need that much vertical room; the
  composite's quarter-panel (~3.4×2.6in) cannot label all 40 rows without overlapping text at any
  readable font size. Resolved by drawing all 40 as unlabeled lollipops (opacity = significance,
  color = direction) and moving the 6 storyboard-specified illustrative category names + values into
  a small side legend rather than inline per-bar labels — this was the single largest legibility
  fix required during assembly (the first draft had 3+ overlapping inline labels).
- **B (Floor structure)**: **new panel**. Study 4's own figure (`fig_paper_S4.py`) shows only 8 of
  the 9 floor measures (it omits `gini_turns`, apparently for space in the original single-figure
  layout). Rebuilt with all 9 from `floor_windows.csv` using the identical within-meeting-r-then-
  Wilcoxon method, so the panel matches the storyboard's "9/9 measures" claim exactly.
- **C (Who opens the floor)**: **new panel**. Study 9's own figure shows initiation lift per
  *individual* member (S1..S5 per team); the storyboard asks for 3 *role* categories (facilitator /
  most-talkative / quietest). Built from `initiation_lift.csv` by identifying, per team, the
  facilitator (flagged), the highest-talk-share non-facilitator member, and the lowest-talk-share
  member. **Post-publication correction**: Study 9's facilitator identification originally used a
  constant raw `speaker_id` that was wrong in 24/34 meetings (see
  `studies/study9_initiators/facilitator_identification.md`); with the corrected, per-meeting-verified
  identity, the permutation test reverses from non-significant ("at chance") to significant in all
  three initiator definitions (p<.01) — the facilitator initiates significantly *less* than talk-time
  predicts. This panel and its caption were regenerated after the correction.
- **D (Affective signature)**: reused Study 12's 8-category lift panel A logic and added a small
  pre/at/post timing inset from `socioemotional_timing.csv` (Study 12's own T4 result), which Study
  12's published figure keeps as a separate panel B — compacted here into one inset per the
  storyboard's "small inset or separate line" instruction.
- **Legibility fix**: Panel C's two teams were originally color-only (teal/orange), which collapse to
  similar gray values — added marker-shape differentiation (circle=Team A, square=Team B) so the
  distinction survives grayscale. Same fix applied to Panel D's timing-inset lines (solid+circle vs
  dashed+square).

## Figure 3 — Temporal structure (4 panels, reused: 3, new: 1)
- **A (Boundaries as perturbations)** and **B (Procedural review > problem-solving)**: reused Study
  6's two panels (`fig_paper_S6.py`) directly — both already matched the storyboard's spec closely.
- **C (Consolidation)**: reused Study 7's baseline-vs-excursion panel (`fig_paper_S7.py` Panel C)
  directly.
- **D (Within-meeting budget)**: **new panel**. No existing figure plots first-half vs second-half
  event rate; Study 10's `fig_early_warning.py` only contains the pre-event-trajectory and ROC
  panels. Built from `meso_halves.csv` (already computed in Study 10's T3) — a simple scatter +
  OLS line, confirming Spearman rho=-.64, p=4.4e-5 pooled across both teams, matching the storyboard's
  cited statistic exactly.
- **Legibility**: clean at first render; Panel D's team markers use circle/square (not just color)
  for the same grayscale reason as Fig 2C/D.

## Grayscale check (all three composites)
Each PNG was converted to grayscale (`PIL.Image.convert("L")`) and visually re-inspected panel by
panel. Result: **pass**, with one class of pre-existing limitation carried from the house style
itself (not introduced here) — teal (`#2E7D8C`) and orange (`#D95F02`) have similar luminance, so any
encoding that relies on *only* that color pair collapses in strict grayscale. Bar charts (Figs 1C,
3A, 3B) remain legible because the two bars are also spatially separated and individually labeled;
scatter/line panels that compare exactly two series by color alone (Fig 2C/D, Fig 3D) were given a
second, shape-based encoding (circle vs square, solid vs dashed) specifically because they had no
other disambiguating cue. Figure 3 Panel C's team-color distinction (baseline/excursion trajectories)
still relies on color only in grayscale; this is a minor, disclosed exception — the panel's primary
story (baseline vs excursion, distinguished by marker+linestyle) survives grayscale intact, and the
secondary "both teams shown" detail is stated numerically in the annotation regardless.

## S11 profile-replication check (per guardrail)
Re-read (not re-run, since no upstream data changed since Study 11 was published/committed)
`study11_replication/data/profile_replication_summary.csv`: taxonomy-fingerprint profile r = **0.9692**
(rounds to .969 as cited in Figure 2A's caption/annotation) — current.

## Outputs
- `fig1_computational_structure.{png,pdf}` (+ generator script)
- `fig2_multilevel_structure.{png,pdf}` (+ generator script)
- `fig3_temporal_structure.{png,pdf}` (+ generator script)
- `_cache_lmin_comparison.py` + `_cache_lmin_det.csv`: helper/cache for Figure 1's L_min inset
  (kept alongside the composite scripts since Figure 1 depends on it; underscore-prefixed to mark it
  as a build dependency rather than a standalone paper figure).
- Supplementary figure: `fig_paper_S11_replication_ledger.{png,pdf,svg}` (already published, S11,
  commit 6f7035a) — no new work, per the brief.
