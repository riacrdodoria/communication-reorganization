# Study 1 — Reconstructing the team-state series from an onset-only transcript

## Correction (2026-10-30, read first)
Earlier versions of this README said that Last-Speaker-Holds (LSH) was "adopted as the turn-taking
substrate throughout". That was wrong. Every metric in Studies 2–13 is computed on multi-speaker team
states reconstructed from utterance onsets with **word-timed durations** (onset + 0.5 s per word, then the
empty state; `src/gorman_reimpl.py`, `METHODS.md` §2). We call this reconstruction **LSH-WD**. The numbers
were right; their description was not. This study now validates the reconstruction that is actually used
and keeps pure LSH as a robustness variant.

## Rationale
Gorman's metrics (%MaxEnt, %DET, RMSE) were developed on laboratory data in which every utterance has a
hand-coded onset and offset, so silence is observed. ASR transcripts of naturalistic meetings give only
the onset, the speaker and the text. The question is which onset-only reconstruction best reproduces the
true silence-preserving ("standard") series.

## Method
**Archival test (`lsh_variants_archival.py`, `lsh_convergent_current_params.py`).** Fifteen sessions of
Gorman et al. (2020) with hand-coded onsets and offsets (7 submarine crews, 8 surgical teams; true silence
share 0–45 %, mean 27.8 %). From each session we keep only what an ASR transcript provides and rebuild the
team state four ways, then compare each with the true standard series under the parameters used
everywhere else (2 Hz grid, 60-s window, 1-s step, %DET L_min = 8, RMSE by the method of analogues with
ε = 3 %DET and a 20-s horizon, events = RMSE > mean + 2.33 SD with 8-s clustering, event match within
±8 s).

| Reconstruction | Rule |
|---|---|
| LSH (pure) | the last speaker holds until the next onset; no silence |
| **LSH-WD** | the speaker holds for 0.5 s per word, then silence (Gorman's 2-words-per-second interpolation) |
| LSH-CAP3 | the speaker holds at most 3 s |
| LSH-CAP10 | the speaker holds at most 10 s |

**Corpus checks (`corpus_lsh_vs_standard.py`, `compute_lsh_metrics.py`).** On the 34 meetings, the
published series compared with (a) the same series LSH-filled and (b) a full pure-LSH recomputation.

## Results
**Archival test** (`results/lsh_variants_summary.csv`, per session in `results/lsh_variants_team.csv`):

| Reconstruction | Entropy r | %DET r | RMSE r | Events matched | Silence share (true 27.8 %) |
|---|---|---|---|---|---|
| LSH (pure) | .91 | .82 | .53 | .51 | 0 % |
| **LSH-WD** | **.97** | **.94** | **.73** | **.65** | 24.0 % |
| LSH-CAP3 | .89 | .92 | .64 | .52 | 54.5 % |
| LSH-CAP10 | .76 | .79 | .42 | .39 | 23.1 % |

The ordering is the same in both domains (submarine LSH-WD .97 / .95 / .73 / .67; surgical .96 / .94 /
.73 / .63). The word-timed rule is the best onset-only approximation on every criterion and also
reproduces the amount of silence. Pure LSH is second on entropy and last on event timing; the session
with no silence gives r = 1.00 for every variant, as it must.

**Corpus checks.** Published versus LSH-filled: median r entropy .94 (min .90), %DET .91 (min .85), RMSE
.78 (min .62), events matched .63 / .61. Published versus pure LSH: entropy .90, %DET .85, RMSE .65;
981 events instead of 913, about half matched (`results/corpus_lsh_vs_standard.csv`,
`results/corpus_lsh_pure_vs_published.csv`). Divergence grows with silence share.

## What this means
- The level of organization (entropy, %DET) is fairly robust to the reconstruction: within-session r ≥ .8
  for pure LSH, LSH-WD and the 3-s cap; only the loose 10-s cap falls below.
- Event timing is reconstruction-dependent: RMSE is a second-order quantity, and about half the threshold
  events of pure LSH have no counterpart within 8 s. This is why the reconstruction must be validated
  rather than assumed, and why the word-timed rule, which matches 65 % of true events, is used.
- The core findings of Studies 2–12 hold when everything is recomputed on pure LSH (supplementary
  robustness run); the weakest under pure LSH are the trigger-class grading of entropy and the
  facilitator's question-initiation result.

## Files
- `lsh_convergent_current_params.py` — archival standard-vs-LSH comparison and the shared metric code.
- `lsh_variants_archival.py` — the four-way reconstruction test (the archival workbooks of Gorman et al.,
  2020, are not distributed; pass their folder as the first argument).
- `corpus_lsh_vs_standard.py`, `compute_lsh_metrics.py` — corpus comparisons.
- `results/` — summary and per-session tables. Per-second archival metric series are not shipped.

## References
Gorman, Cooke, Amazeen & Fouse (2012); Cooke, Gorman, Myers & Duran (2013); Gorman et al. (2020).
See `references.md`.
