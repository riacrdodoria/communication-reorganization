# Study 6 — Dialogue microstructure: topic episodes and the meeting arc

## Rationale and gap
Fixed 90 s windows straddle topic boundaries and dilute the taxonomy/process signal. This study moves to
an **ecological** unit — the *topic episode* (a discussion unit; "episodes" in the team-process sense of
Marks, Mathieu & Zaccaro 2001; topic/discourse segmentation in the sense of Hearst 1997). Doing so
reveals that reorganization is a topic-**transition** phenomenon and that meetings follow a recurring
discussion arc.

## Method
**Segmentation (two methods, validated).** Unsupervised TextTiling on TF-IDF utterance vectors for all
meetings (`gen_fine_episodes.py`, `topic_segment.py`); a model-based segmentation on a subset, with topic
labels; agreement quantified by boundary F1 and WindowDiff against a random baseline
(`validate_segmentation.py`).

**Granularity sweep** (`granularity_sweep.py`). Across target episode lengths, finer episodes capture more
taxonomy structure (η² excess over random boundaries), while coarser episodes give more reliable per-
episode metrics; the boundary effect is robust at all scales. Fine episodes (≈ 18 utterances) are used
for the taxonomy work (`data/episodes_fine.csv`).

**Episode-level coding.** All six taxonomies (41 categories) re-coded per fine episode for all meetings
(`data/codebooks_episode/`; consolidated in `results/episode_codes.csv`).

**Protocol-anchored segmentation (EOS Level 10).** These meetings run the EOS *Level 10 Meeting* agenda
(Wickman, *Traction* 2011): a fixed seven-stage script (segue → scorecard → rock review → headlines →
to-do review → IDS problem-solving → conclude). Each stage's opening was annotated with a verbatim quote
against a fixed protocol (`l10_protocol.md`) and mapped to a timestamp (0/34 unmappable), giving a third,
theory-driven segmentation alongside the windows and the data-driven episodes (`l10_analysis.py`,
`l10_taxonomy.py`). (Stage-boundary timestamps are derived from the withheld transcripts; only the
resulting numeric per-stage tables are published.)

**Analyses.** Reorganization at boundaries vs episode interiors (`episode_analysis.py`); the episode-level
fingerprint (`episode_fingerprint.py`); and an episode typology (`episode_typology.py`,
`figures/fig_meeting_arc.png`).

## Results
- **Topic boundaries are reorganization events** — the naturalistic perturbation. In ±30 s of a boundary
  vs episode interior, entropy ↑ and %DET ↓ (e.g. unsupervised, 34 meetings: Δentropy ≈ +9.5, Δ%DET ≈
  −11.9, p < .001), replicated across both segmentation methods. The effect is **non-circular**: boundaries
  come from content/semantics, the metrics from turn-taking only. This reconnects Gorman's
  perturbation→reorganization paradigm to naturalistic data.
- **A recurring meeting arc.** A soft typology (five discussion types; silhouette ≈ 0.09, i.e. a
  continuum of tendencies) ordered by within-meeting position: **opening / procedural Q&A** (most
  reorganized) → **status / information-sharing** → **problem / debate** (highest entropy) → **solution
  exploration / co-construction** (most deliberative) → **closing / socio-emotional**. Discussion types
  map onto reorganization state.
- **The fingerprint is a boundary phenomenon.** At the episode level, the deliberation↔coordination
  directions replicate but no category is individually significant: averaging the metric over a whole
  episode smooths away the reorganization, which lives at the boundaries. Reorganization is thus a
  transition phenomenon; episodes are the right unit for discussion *type*, boundaries/windows for
  reorganization and its content.
- **The EOS Level 10 agenda externalises the axis.** Meetings adhere to the protocol (IDS and conclude in
  34/34; segue/to-do near-universal; scorecard/rock ~3/4; headlines most-skipped; IDS ≈ 63% of meeting
  time) — an applied/external-validity anchor. Crossing stages with the metrics gives a robust,
  counterintuitive result: the procedural **review** stages (scorecard/rock/to-do) reorganize *more* than
  the problem-solving **IDS** (per-meeting paired Wilcoxon, n = 32: entropy 37.6 vs 33.5, Δ = +4.1,
  p = .001; reorg-event rate 4.2% vs 2.7%, Δ = +1.5, p = .009; %DET −1.5, n.s.). The content cross
  explains it: of 41 taxonomy categories, 23 differ between review and IDS (paired Wilcoxon, BH-FDR), and
  IDS is the deliberative pole — arguable, exploratory talk, opinion, negotiation, and solution
  construction all enriched there, while the review stages carry non-arguable status reporting and
  information-giving. Deliberative *content* concentrates the floor on one reasoner (F1); procedural
  content spreads it across rapid multi-party exchange (F2). Lexical content and turn-taking — independent
  signals — converge on the axis from opposite sides (`figures/fig_l10_stages.png`).
- **The three segmentations converge.** (A) The data-driven episode *types* land on the L10 *stages* they
  should — χ²(24) = 432, p = 1.6e-76, Cramér's V = 0.34: solution-exploration episodes are 81 % in IDS,
  problem/debate 68 % in IDS, opening/procedural 39 % in the segue, closing 47 % in conclude. The
  unsupervised typology recovers the agenda without seeing it. (B) Topic-episode boundaries co-locate with
  L10 stage onsets above chance: 32 % of L10 onsets have an episode boundary within ±15 s vs 15 % under a
  within-meeting circular-shift null (paired Wilcoxon p = 7e-6).
- **L10 stage transitions are perturbations.** ±30 s of a stage onset vs interior (paired Wilcoxon, 34
  meetings): entropy +8.0 (p = 3.6e-8), %DET −7.3 (p = 5.0e-7) — the same magnitude as topic-episode
  boundaries. IDS-entry is sharper (entropy +9.8, %DET −9.6, both p < .001). This resolves the apparent
  tension above: *entering* IDS spikes reorganization, but the IDS *interior* — the long deliberative
  block — settles into the most concentrated, lowest-reorganization regime. Reorganization is a transition
  phenomenon; the deliberative interior is where the floor concentrates.

## Honest scope
Segmentation is noisy (moderate, above-chance agreement); the model-based segmentation is the higher-
quality instrument and the unsupervised method corroborates that boundaries are real. The typology is a
soft clustering (a continuum). Per-episode metrics are noisy (≈ 16 utterances/episode). Episode-level
annotation should be validated against a human-coded subset before publication. The L10 stage labels are
annotator-assigned and need the same validation; advisor-led sessions deviate from the textbook L10
(stages merged, skipped, reordered, or re-entering IDS — handled by aggregating duplicate stage labels).
The within-meeting `reorg-event rate` baseline is dominated by IDS (≈ 63 % of time), so it measures which
stages spike above that baseline, consistent with the entropy result.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `gen_fine_episodes.py` | transcripts | `data/episodes_fine.csv` | **yes** |
| `topic_segment.py` | transcripts | `data/episodes_unsup.csv` | **yes** |
| `validate_segmentation.py` | episode boundaries | console | no |
| `granularity_sweep.py` | transcripts + metrics + taxonomy counts | console | **yes** |
| `episode_analysis.py` | episode boundaries + metrics | console | no |
| `episode_fingerprint.py` | `results/episode_codes.csv` | console | no |
| `episode_typology.py` | `results/episode_codes.csv` | updates `results/episode_codes.csv` | no |
| `fig_meeting_arc.py` | `results/episode_codes.csv` | `figures/fig_meeting_arc.png` | no |
| `l10_analysis.py` | L10 stage annotations + metrics | `results/l10_stage_metrics.csv` | **yes** |
| `l10_taxonomy.py` | L10 stage annotations + `results/episode_codes.csv` | `results/l10_taxonomy_rates.csv`, `results/l10_taxonomy_review_vs_ids.csv` | **yes** |
| `fig_l10.py` | `results/l10_stage_metrics.csv` + `results/l10_taxonomy_review_vs_ids.csv` | `figures/fig_l10_stages.png` | no |
| `l10_convergence.py` | L10 stage annotations + `results/episode_codes.csv` | `results/l10_convergence_typestage.csv` | **yes** |
| `l10_boundary.py` | L10 stage annotations + metrics | `results/l10_boundary_panel.csv` | **yes** |

`l10_protocol.md` — the EOS Level 10 agenda definitions and stage-annotation instructions.
The L10 stage annotations themselves carry verbatim transcript snippets and are withheld with the
transcripts; the published `results/l10_*.csv` are numeric only.

`codebook_defs.md` (in `study3_content_fingerprint/`) — the same 41-category definitions used for episode coding.

## References
Hearst (1997); Marks, Mathieu & Zaccaro (2001); Gorman & Hessler et al. (2012); Wickman (2011, *Traction* /
EOS Level 10 Meeting); Pangakis et al. (2023). See `references.md`.
