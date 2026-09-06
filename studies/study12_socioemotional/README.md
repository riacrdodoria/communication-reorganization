# Study 12 — The socioemotional signature of reorganization

## Rationale and gap
The six-taxonomy content layer (Study 3) already codes 41 categories per window, including
socioemotional content (Bales IPA's positive/negative quadrants; act4teams' full-scheme
positive/negative facets), but the fingerprint analysis treats all categories in one family and has
never examined the socioemotional dimension on its own terms — a core interest in the meeting-science
literature (humor, support, positivity dynamics; Lehmann-Willenbrock, Allen & Kauffeld, 2013). This
study isolates that layer and asks: are reorganization events accompanied by warmth (laughter,
agreement, solidarity), by tension (disagreement, antagonism), or are they affectively neutral,
procedural passages? Either answer sharpens Study 2/3: a socioemotional signature adds a relational
mechanism to the floor-opening account; a neutral result strengthens "coordination, not deliberation
(and not affect)."

## Method
**T1 — Category map.** Every category across all six coded taxonomies is classified as a genuine
affect-display code (with valence) or excluded with a stated justification tied to the scheme's own
published definition (`results/socioemotional_map.csv`, 45 rows). The **confirmatory family** (8
categories): Bales IPA (1950) socioemotional-positive (`bsolid` shows solidarity, `btension` tension
release/jokes, `bagree` agrees) and socioemotional-negative (`bdisagree` disagrees, `btensh` shows
tension, `bantag` shows antagonism); act4teams-full (Lehmann-Willenbrock & Kauffeld, 2018)
facet-level `pos`/`neg` (a *second, independently-coded* pass, `data/act4teams/`). Two act4teams-SHORT
categories (`coop` praising/thanking, `cprod` backbiting/complaining) are affect-*adjacent* but
excluded from the confirmatory family (would double-count with `bsolid`/`pos` and `bantag`/`neg`);
reported separately using their existing Study 3 result, not re-tested. Two proposed coding-free
lexical markers (typed laughter conventions; exclamation density) were searched across all 34
transcripts (17,488 utterances) and returned **essentially null data** (1 laughter match, 1 exclamation
mark, total) — documented as a genuine boundary condition (this is an ASR transcript of spoken audio,
not a chat log) rather than forced into a proxy.

**T2 — Event-locked lift.** Same machinery as the main content fingerprint (Study 3): per-meeting
density lift at RMSE reorganization events (>mean+2.33 SD) vs. baseline seconds, Wilcoxon signed-rank
across meetings, BH-FDR **within** the 8-category family (never folded into the original 40-category
family). Also split by Study 9's event classification (TRANSITION / INTERIOR_HANDOFF /
INTERIOR_OTHER), at the coding's native 90 s window grain.

**T3 — Positive vs. negative asymmetry.** Paired Wilcoxon on per-meeting composite lift (mean of the
4 positive vs. 4 negative categories). Review-vs-IDS contrast (EOS L10 procedural-review stages vs.
the deliberative IDS block) for each of the 8 categories, paired Wilcoxon + BH-FDR.

**T4 — Timing within the event.** Pre-onset / onset / post-onset window density (90 s grain — the
coding's native resolution, coarser than the ±30 s used for second-resolution metrics elsewhere in
this program; disclosed, not hidden), with a circular-shift null (2,000 seeded rotations per
METHODS.md §6 convention).

## Results
- **Reorganization has a positive, not a negative, socioemotional face.** `bagree` (+0.266),
  `pos` (+0.198), and `bsolid` (+0.142) all rise significantly at events (BH-FDR q ≤ .001, 26–31/34
  meetings same-direction; family of 7 after `bantag` is excluded as too rare, 10/34 meetings); no
  negative category survives FDR (`btensh` closest, q = .055 n.s.). (Corrected 2026-09-05: one
  act4teams coding file had its windows keyed 30 s off the 90-s grid, so 39 % of that meeting read as
  zero affect; windows are now snapped to the grid.) The positive-vs-negative composite
  asymmetry is itself significant (paired Wilcoxon p=1.06e-4, 27/34 meetings positive>negative).
- **A third, independent coding corroborates this without being folded into the family test**:
  act4teams-SHORT's `coop` (praising/thanking) already shows a strong lift in Study 3's original test
  (+0.168, q<.0001), while `cprod` (backbiting) does not (n.s.) — the same positive-not-negative
  pattern from a third coding pass.
- **The positive signature is a sharp spike coincident with the event, not a lubricant or a repair.**
  Positive-composite density rises pre→onset and falls onset→post (circular-shift p = .001 and
  p < .0005, 2,000 shifts); the negative composite rises into the event but does **not** significantly
  recede afterward. At the 90-s grain "coincident" cannot be separated from "within 90 s before".
- **`bagree` is somewhat concentrated at topic/agenda TRANSITIONs** (Kruskal-Wallis H = 10.5,
  q = .041; TRANSITION 1.44 > HANDOFF 1.30 ≈ OTHER 1.27 per window) — the only category surviving FDR
  in the event-class split, and a weaker contrast than first reported (the class split now uses the
  shared classification rule, `METHODS.md` §4).
- **IDS (deliberation), not the procedural review, is where tension concentrates**: `bdisagree`,
  `neg`, and `bantag` are all *higher* in IDS than in review stages (BH-FDR q = .016, .016, .048);
  the `bantag` test rests on only 7 non-zero meeting pairs (column `n_nonzero` in
  `results/socioemotional_review_vs_ids.csv`) and is not counted as a headline; no positive category
  differs by stage. Stage windows are assigned by their start time, so the window straddling a stage
  boundary belongs to the earlier stage (34 such windows; midpoint assignment gives q .038 / .038 / .048).
- **Two proposed lexical markers returned null data**, honestly reported as a boundary condition of
  this ASR-transcribed, spoken corpus, not as a design failure.

Full statistics, honest caveats, and the paper-ready paragraph: `RESULTS.md`.

## Honest scope
- The confirmatory family is 8 categories (not the originally-proposed 10): the 2 lexical markers
  returned null data and are reported separately, not tested; `bantag` could not be included in the
  main paired test (too rare) though it does contribute to the review-vs-IDS test (event-independent).
- T4's timing analysis operates at the coding's native 90 s window grain — a real resolution limit,
  not a finer ±30 s test; stated explicitly rather than implied.
- 2 teams, 34 meetings — replication, not generalization, as throughout this program (no per-team
  split was run here; this study reports the pooled family test, consistent with Study 3's original
  approach).

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `src/socioemotional_map.py` | — (hardcoded, documented mapping) | `results/socioemotional_map.csv` | no |
| `src/lexical_markers.py` | transcripts | `results/lexical_marker_diagnostic.csv`, `results/lexical_marker_face_validity.md` | **yes** |
| `src/build_socioemotional_lifts.py` | metrics + codebooks2 + act4teams + Study 9 events | `results/socioemotional_lifts.csv`, `results/socioemotional_by_class.csv` | no |
| `src/socioemotional_asymmetry.py` | metrics + codebooks2 + act4teams + L10 stages | `results/socioemotional_pos_vs_neg.csv`, `results/socioemotional_review_vs_ids.csv` | **yes** (L10 quote-to-timestamp mapping) |
| `src/socioemotional_timing.py` | codebooks2 + act4teams + Study 9 events | `results/socioemotional_timing.csv` | no |
| `../../paper_figures/fig_paper_S12.py` | all of the above | `../../paper_figures/fig_paper_S12_socioemotional.{png,pdf,svg}` | no |

All published outputs are numeric only. `results/lexical_marker_face_validity.md` reports the 2
lexical matches as matched-token + non-content metadata (meeting id, utterance word count, position)
only — never the surrounding sentence — per this program's hard rule that raw transcript text never
appears in the public repo, even pseudonymized.

## References
Bales, R. F. (1950). *Interaction Process Analysis*. Addison-Wesley. Lehmann-Willenbrock, N., &
Kauffeld, S. (2018). The advanced interaction analysis for teams (act4teams) coding scheme.
Lehmann-Willenbrock, N., Allen, J. A., & Kauffeld, S. (2013). A sequential analysis of procedural
meeting communication. *Journal of Applied Communication Research*. Klünder et al. (2020) for
act4teams-SHORT. Benjamini & Hochberg (1995). This program's Studies 2, 3, 6, 9 (event definition,
content-fingerprint machinery, L10 stage boundaries, event classification). See `references.md`.
