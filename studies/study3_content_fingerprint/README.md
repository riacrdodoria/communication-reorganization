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

**Coding-free triangulation.** Fourteen label-free text-dynamics measures per 90 s window
(`triangulation_build.py` → `results/triangulation_windows.csv`; tested in `triangulation_test.py`,
`triangulation_figure.py`): semantic recurrence (TF-IDF / conceptual recurrence), turn-to-turn coherence,
topic-shift novelty, lexical diversity, connective density, content-word overlap, and structural turn
statistics. An embedding-based version (`embed_recurrence.py`) provides a representation-robustness check.

**Instrument-rigour checks.** Language Style Matching with the BP-LIWC2015 dictionary (`liwc_lsm.py`) and
a broader LIWC psychological-category map (`liwc_map.py`), each computed **raw and controlling for turn
length** (`METHODS.md` §7).

## Results
- **Reorganization = coordination, not deliberation.** Across all six taxonomies, reorganization events
  are enriched in coordinative/procedural talk (non-argument, feedback, questions, requests, agreement,
  convergence, structuring) and depleted in deliberative talk (argument, opinion-giving, exploratory
  reasoning, knowledge co-construction, transactive linking). Coverage: **28 of 40 testable categories
  significant (70%)**, with no contradictions.
- **Coding-free corroboration.** 13 of 14 label-free measures track reorganization coherently with no
  coding. Headline cross: semantic recurrence vs turn-taking %DET, within-meeting r ≈ **+0.43** — content
  and speaker repetitiveness destabilise together. The embedding version agrees in direction (r ≈
  0.41–0.57), confirming the result is not specific to TF-IDF.
- **Instrument corrections (reported transparently).**
  - The earlier "RMSE = argument/disagreement" reading was an **artefact** of the mis-specified RMSE
    (Study 2); the Gorman-faithful RMSE tracks floor distribution.
  - Language Style Matching computed with curated word lists appeared strong, but with the **official
    BP-LIWC2015** dictionary it is weak, and a partial-correlation analysis shows the apparent effect was
    a **turn-length confound** (curated-LSM correlates r ≈ +0.60 with turn length; controlling for turn
    length collapses its association with %DET from +0.35 to −0.11). LSM is therefore not retained as a
    reorganization signal.
  - In the broader LIWC map, **22 of 25** categories were turn-length artefacts; only three (differ,
    cause, risk) survive the turn-length control, with modest effect sizes.

The robust content signals are therefore the validated-taxonomy fingerprint and the semantic-recurrence /
coherence / novelty family.

## Scripts
| script | reads | writes | needs transcripts? |
|---|---|---|---|
| `peaks_taxonomy_sig.py` | metrics + taxonomy counts | `results/peaks_taxonomy_sig.csv` | no |
| `gorman_vs_content.py` | metrics + taxonomy counts | console | no |
| `triangulation_build.py` | transcripts + metrics | `results/triangulation_windows.csv` | **yes** |
| `triangulation_test.py` / `triangulation_figure.py` | `results/triangulation_windows.csv` | console / `figures/fig_triangulation.png` | no |
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
