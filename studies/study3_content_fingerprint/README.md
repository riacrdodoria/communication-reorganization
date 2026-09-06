# Study 3 — The content fingerprint of reorganization

## Rationale and gap
Reorganization metrics are mechanical (turn-taking only); their substantive meaning is undertheorised.
This study asks **what reorganization corresponds to** by relating reorganization events to validated
interaction taxonomies, and then defends the result against the obvious objection — that it is an
artefact of one coding scheme — by reproducing it with measures that need **no** human or model coding.

## Method
**Taxonomy fingerprint.** Six previously validated coding schemes — CACS, Gunawardena IAM, Mercer talk
types, Bales IPA, act4teams-SHORT, ISO 24617-2 — coded per 90 s window (definitions: `codebook_defs.md`;
annotation per `METHODS.md` §5). At reorganization events (RMSE peaks / %DET valleys), the density of each
category is compared with baseline within each meeting and combined across meetings (Wilcoxon, BH-FDR;
`peaks_taxonomy_sig.py`).

**Coding-free triangulation.** Fifteen label-free text-dynamics measures per 90 s window
(`triangulation_build.py` → `results/triangulation_windows.csv`; tested in `triangulation_test.py` →
`results/triangulation_Z.csv`; `triangulation_figure.py`): semantic recurrence and semantic %DET (TF-IDF /
conceptual recurrence), turn-to-turn coherence, topic-shift novelty, lexical diversity, connective density,
content-word overlap, two Language-Style-Matching variants (curated list; BP-LIWC2015), and structural turn
statistics. **Every measure is tested raw and after partialling out turn length within meeting**
(`METHODS.md` §7; joint turn-length + turns-per-window control reported as a sensitivity bound), because
utterance segmentation is the very turn structure the turn-taking metrics are built from. An
embedding-based version (`embed_recurrence.py`) provides a representation-robustness check.

**Instrument-rigour checks.** Language Style Matching with the BP-LIWC2015 dictionary (`liwc_lsm.py`) and
a broader LIWC psychological-category map (`liwc_map.py`), each computed **raw and controlling for turn
length** (`METHODS.md` §7).

## Results
- **Reorganization = coordination, not deliberation.** Across all six taxonomies, reorganization events
  are enriched in coordinative/procedural talk (non-argument, feedback, questions, requests, agreement,
  convergence, structuring) and depleted in deliberative talk (argument, opinion-giving, exploratory
  reasoning, knowledge co-construction, transactive linking). Coverage: **28 of 40 testable categories
  significant (70%)**, with no contradictions.
- **Coding-free corroboration — corrected (2026-09-05).** Raw, 13 of 15 label-free measures track
  reorganization, with semantic recurrence vs turn-taking %DET at within-meeting r = +0.43 (Stouffer
  Z = +19.5). That headline **does not survive the turn-length control**: semantic recurrence Z = −1.8,
  turn-to-turn coherence Z = −0.05 (both n.s.), because TF-IDF recurrence among utterances is denser when
  utterances are long and few (within-meeting r with turn length = +0.66) and turn length is itself tied
  to %DET (r = +0.68). The measures that survive the control in the reorganization direction are
  **novelty / topic-shift** (Z vs %DET −3.9 controlled, −14.0 raw), **semantic %DET** (−3.9 controlled;
  null raw) and content-word overlap (−3.1). Word entropy, type-token ratio, hapax ratio and both LSM
  variants reverse sign under the control (e.g. LSM-LIWC +4.0 raw → −7.2 controlled), i.e. they were
  suppressed by turn length and, once it is removed, indicate *more* style matching and *more* lexical
  concentration at reorganization; these reversals are reported but not built on. The embedding version
  agrees in direction with the raw TF-IDF measures (r ≈ 0.41–0.57) and shares their confound.
- **Instrument corrections (reported transparently).**
  - The earlier "RMSE = argument/disagreement" reading was an **artefact** of the mis-specified RMSE
    (Study 2); the Gorman-faithful RMSE tracks floor distribution.
  - Language Style Matching computed with curated word lists appeared strong, but with the **official
    BP-LIWC2015** dictionary it is weak, and a partial-correlation analysis shows the apparent effect was
    a **turn-length confound** (curated-LSM correlates r ≈ +0.60 with turn length; controlling for turn
    length collapses its association with %DET from +0.35 to −0.11). LSM is therefore not retained as a
    reorganization signal.
  - In the broader LIWC map, of 16 categories significant raw, **13 collapse under the turn-length
    control**; three (differ, cause, risk) survive with modest effect sizes; the remaining 9 of 25 were
    null throughout. (An earlier "22 of 25 were artefacts" conflated the never-significant with the
    collapsed.)
  - The published `results/triangulation_windows.csv` had at one point carried the BP-LIWC2015 LSM in the
    column named `lsm` by a manual overwrite; the build script now writes `lsm_curated` and merges
    `liwc_lsm` explicitly, and the figure shows the LIWC variant under its own name.

The robust content signals are therefore the validated-taxonomy fingerprint (unchanged by any of the
corrections: 28/40 at RMSE peaks, 27/40 at %DET valleys, 33/41 peak-vs-valley phase contrast) and, among
coding-free measures, novelty / topic-shift. Semantic recurrence and coherence are turn-length proxies
in this corpus and are no longer cited as content evidence.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `peaks_taxonomy_sig.py` | metrics + taxonomy counts | `results/peaks_taxonomy_sig.csv` | no |
| `gorman_vs_content.py` | metrics + taxonomy counts | console | no |
| `triangulation_build.py` | transcripts + metrics | `results/triangulation_windows.csv` | **yes** |
| `triangulation_test.py` | `results/triangulation_windows.csv` | `results/triangulation_Z.csv` (raw, turn-length-controlled and joint-controlled Stouffer Z, BH q) | no |
| `triangulation_figure.py` | `results/triangulation_Z.csv` | `figures/fig_triangulation.png` (hollow = raw, filled = controlled) | no |
| `embed_recurrence.py` | transcripts + metrics | `embedding_windows.csv` | **yes** |
| `liwc_lsm.py` | transcripts + metrics + BP-LIWC2015 dict | `results/liwc_lsm_windows.csv` | **yes** + licensed dict |
| `liwc_map.py` | transcripts + metrics + BP-LIWC2015 dict | `results/liwc_map_windows.csv` | **yes** + licensed dict |
| `phase_taxonomy_full.py` | metrics + taxonomy counts | console | no |

`codebook_defs.md` — the verbatim definitions of all 41 categories across the six taxonomies.

## A note on the BP-LIWC2015 dictionary
The Brazilian-Portuguese LIWC2015 dictionary (Carvalho et al. 2024) is licensed by its authors and is
**not** included here. To run `liwc_lsm.py` / `liwc_map.py`, obtain it from the authors and point the
`LIWC_DIC` environment variable at your local copy. The provided outputs contain only numeric scores.

## References
Canary, Brossmann & Seibold (1987); Gunawardena, Lowe & Anderson (1997); Mercer (2000); Bales (1950);
Klünder et al. (2020); ISO 24617-2; Angus, Smith & Wiles (2012); Fusaroli & Tylén (2016); Ireland &
Pennebaker (2010); Carvalho et al. (2024); Pangakis et al. (2023). See `references.md`.
