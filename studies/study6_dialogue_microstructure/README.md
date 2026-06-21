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

## Honest scope
Segmentation is noisy (moderate, above-chance agreement); the model-based segmentation is the higher-
quality instrument and the unsupervised method corroborates that boundaries are real. The typology is a
soft clustering (a continuum). Per-episode metrics are noisy (≈ 16 utterances/episode). Episode-level
annotation should be validated against a human-coded subset before publication.

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

`codebook_defs.md` (in `study3_content_fingerprint/`) — the same 41-category definitions used for episode coding.

## References
Hearst (1997); Marks, Mathieu & Zaccaro (2001); Gorman & Hessler et al. (2012); Pangakis et al. (2023).
See `references.md`.
