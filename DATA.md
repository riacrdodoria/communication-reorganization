# Data: description, anonymisation, and availability

## Availability statement

The raw meeting transcripts contain confidential participant speech and are **withheld**. To keep the
research fully auditable without exposing them, this repository ships only **numeric** derivations from
which the analyses can be checked but the original speech cannot be reconstructed. Speakers appear only
as anonymous integer identifiers; any personal names that occurred in the audio were replaced by neutral
placeholders during anonymisation. The BP-LIWC2015 dictionary used in Study 3 is licensed (Carvalho et
al. 2024) and is not redistributed.

## What is included

### `data/metrics_gorman_l8/` — reorganization metric series (34 files)
One CSV per meeting, named `<meeting_id>_gorman.csv`. Columns:
- `second` — window-centre time (s)
- `entropy_g` — %MaxEnt entropy of the team state (0–100)
- `det_g` — percent determinism, L_min = 8 (0–100)
- `rmse_g` — nonlinear-prediction RMSE on the %DET series

### `data/codebooks/`, `data/codebooks2/` — taxonomy counts per 90 s window
JSON per meeting: `{meeting_id, window_s, windows: [{t, <category>: count, ...}]}`. `codebooks/` holds the
act4teams-SHORT and ISO 24617-2 categories; `codebooks2/` holds the CACS, IAM, Mercer, and Bales
categories. Values are integer act counts; **no text** is stored.

### `data/codebooks_episode/` — taxonomy counts per topic episode (34 files)
JSON per meeting: `{mid, episodes: [{ep, utt_start, utt_end, n_utt, codes: {<41 categories>: count}}]}`.
Boundaries are utterance indices; values are counts; **no text** is stored.

### `data/episodes_fine.csv`, `data/episodes_unsup.csv` — episode boundaries
One row per episode: `mid, ep, utt_start, utt_end, n_utt` (and second ranges where applicable). Utterance
indices and timestamps only.

### `results/` — result tables produced by the analyses
Numeric per-window / per-episode / per-meeting tables and the combined statistics reported in each study
(e.g. `triangulation_windows.csv`, `floor_windows.csv`, `longitudinal_panel.csv`, `episode_codes.csv`,
`peaks_taxonomy_sig.csv`). See each study README for which script writes which table.

### `figures/` — all figures (PNG).

### `results/speaker_roles_verified.csv` — per-meeting speaker role map
`mid, team, raw_id, role, n_utt, n_words`. Roles: FACILITATOR (the same external advisor in every
meeting), A1–A3 / B1–B3 (team members, fixed roster order; B2 appears under a shared team account in nine
meetings and under a personal account in the other eight, both mapped to B2), BOT (the transcription tool's announcement line, removed from the canonical transcripts and from the
metrics on 2026-09-05; kept in the map for traceability). Because `speaker_id` is assigned per meeting
by order of first appearance, this map is the only valid way to follow a person across meetings.

## Meeting identifiers

A meeting id encodes the date and team, e.g. `2024.10.14startup_a`. The two teams are anonymised as
*Team A* and *Team B*. Onsets are at whole-second resolution; no sub-second timing exists in the source,
which is why %DET is de-saturated via L_min rather than via finer timing (see `METHODS.md`).

## Files needed to re-run text-based scripts

Scripts that compute taxonomy or text-dynamics measures read the withheld transcript files
(`data/text_startup/<meeting_id>_transcript.csv`, columns `onset_seconds, speaker_id, text`). These are
not provided; the **outputs** of those scripts are provided in `data/` and `results/` so the results
remain auditable. Each study README marks which scripts require the transcripts.
