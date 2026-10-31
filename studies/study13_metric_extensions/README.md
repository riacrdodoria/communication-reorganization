# Study 13 — Metric extensions: system type, early warning, turn allocation, routinization, and content

## Rationale and gap
Studies 2–12 describe reorganization with the three Gorman/Grimm metrics (%MaxEnt, %DET, RMSE events).
Wiltshire (2026, *Small Group Research*) asks for three things this program had not yet done systematically:
(1) placing a team in a dynamical-systems typology rather than describing excursions, (2) comparing
metrics to learn which are interchangeable, and (3) following trajectories across time scales.
Gorman and Wiltshire (2024) give the typology: System I (fixed point), II (periodic), III (changing
periodic). This study runs, on the same 34 meetings and the same substrate, a set of quantitative
extensions that need no human or model-based content coding. Every test uses the **run-shuffle null**
(the order of team-state runs is permuted; each state's total time and the run-length distribution are
kept), which is stricter than the AR(1)/VAR(1) surrogates of Study 2 because it holds the turn-length mix
fixed.

## Method (one script per item; all read `~/lsh-work` locally, write numeric outputs to `results/`)
Substrate: `data/metrics_gorman_l8` and the 2 Hz team-state series of `src/gorman_reimpl.py`
(multi-speaker states reconstructed from onsets with word-timed durations; see `METHODS.md` §2 and
Study 1). Events: the 913 RMSE events of Study 9 (`events_initiators.csv`). Shared loaders: `common.py`.

| Item | Script | What it tests |
|---|---|---|
| Run-shuffle check of Study 2 | `runshuffle_study1.py` | excursion amplitude, number of peaks, series SD vs 200 run-shuffled corpora |
| Typology between meetings | `typology.py` | System I/II/III per meeting (periodicity 1–5 min in thirds, 200 surrogates) |
| Typology within meetings | `system_within.py` | 10-min segments, step 5 min, 100 surrogates per segment |
| Which cut? | `system_cuts.py` | periodicity under 5/10/20-min windows and L10 stages; fixed-point relocation (eta²) by stage and topic episode; blind PELT change points and their alignment with boundaries |
| Critical slowing down | `csd.py`, `csd_gap.py` | rolling variance and lag-5 autocorrelation trends before events vs matched baselines; `csd_gap.py 30` is the leakage-free version |
| Event rhythm | `rhythm.py` | burstiness, memory, Allan factor of event onsets |
| Routinization | `routinization.py` | Markov entropy rate of speaker transitions and member-to-member transitions across weeks |
| Metric battery | `battery.py` | 11 window metrics (incl. RR, LAM, TT, LZ76, conditional entropy): correlation, PCA, event and boundary sensitivity |
| Multiscale | `multiscale.py` | window sweep 15–240 s; DFA; multiscale sample entropy |
| Turn allocation | `rem.py` | relational-event (conditional-logit) model of who takes the next turn; moderation by events, IDS stage, week |
| State space grid | `ssg.py` | active speakers × top-speaker share grid by stage and near events |
| Artifact checks | `rem_artifacts.py`, `routinization_artifacts.py` | turn-allocation effects near events controlled for local entropy, with placebo entropy peaks and a circular-shift null; routinization decomposed into participation concentration vs transition structure, with attendance and tool-change controls (`meeting_covariates.csv`) |
| Change-point anatomy | `cp_anatomy.py` | what PELT level shifts are: size vs shuffle, long-turn boundaries, dominant speaker, content, events |
| Floor states and the two clocks | `floor_cycle.py` | F1/MIX/F2 floor states at each boundary type; long-turn ends, novelty and lexical uptake; two origins of topics; centralization and boundary rates in 5-min blocks; the two clocks by stage |
| Topic triangulation | `topic_semantics_cache.py`, `topic_triangulation.py`, `topic_llm_check.py` | topic boundaries from sentence embeddings (multilingual MiniLM), a lemma co-occurrence semantic network (spaCy pt, Louvain communities) and semantic-network change, against the original lexical tiling, the agenda and an earlier LLM segmentation; text-shuffle null; topic-transition markers and pauses as independent cues |
| LLM topic segmentation (all 34 meetings) | `llm_topics_PROTOCOL.md`, `llm_topics_analysis.py` | one LLM agent per meeting with identical instructions, content only (row numbers and text; no speakers or times), topics and subtopics with kind and confidence; validated against the agenda, the other segmentations, transition markers, pauses and semantic shift; floor state and reorganization events by topic kind. Labels are not distributed. |
| Divisions of meeting time | `partitions.py` | co-occurrence of six boundary sets (agenda stage, topic, event, level shift, extended floor turn, novelty peak) vs circular shifts |
| Content (label-free) | `content.py` | TF-IDF lexical novelty, topic entropy (KMeans), cross-speaker uptake; turn-length controlled |

## Headline results (details and all numbers in `RESULTS.md`)
- **Correction to Study 2.** Against the run-shuffle null the peak-excursion amplitude is *not* beyond
  chance (SD 14.82 vs 12.94 [9.72, 16.56], p = .169). What exceeds the null is the **number** of entropy
  peaks (49 vs 25.4, p = .005), and the series is slightly more regulated than its shuffles (SD 17.41 vs
  18.25). The amplitude reflects the turn-length mix; the temporal organization is in how often
  excursions occur and where they occur.
- **System I everywhere, with a moving setpoint.** 33/34 meetings are System I. Within meetings, the
  share of periodic segments never exceeds the 5 % chance rate under any cut (5, 10, 20 min, or agenda
  stage). But the fixed point **relocates**: agenda stages and topic episodes explain more entropy
  variance than in run-shuffled meetings (eta² .097 vs .055, p = 4e-4; .368 vs .281, p = 9e-7). Blind
  change-point detection does not recover this structure, so the meeting's own units (stage, topic,
  event) are the right cuts and fixed windows are only a robustness check.
- **Early warning.** Rolling variance of %DET rises before events (with a 30-s gap so that no centred
  metric window touches post-onset data: 32/34 meetings, p < .0001; lag-5 autocorrelation 25/34,
  p = .0004; still present with a 60-s gap). Entropy shows no such signal. This extends Study 10, whose
  slope features were partly definitional.
- **Retracted after artifact checks: "the floor opens at reorganization" and "routinization in both teams".**
  The weaker reciprocity and facilitator advantage near events vanish once local entropy is controlled
  (interaction ORs .998 and .962; non-event entropy peaks show the same raw pattern; circular-shift null
  p = .59 and .27): high-entropy stretches are by definition distributed talk. The declining transition
  entropy is explained in Team A by absences, rising facilitator share and the last meetings (no trend in
  weeks 1–12, no change in structure beyond participation shares) and in Team B mainly by the facilitator
  concentrating turns, with a modest rise in structure beyond shares (τ = +.38, p = .034).
- **What the blind change points are.** PELT level shifts are as frequent as in run-shuffled meetings and
  *smaller* (26.2 vs 29.3 %MaxEnt); 54 % fall within 15 s of the start or end of an extended floor turn
  (≥ 30 s) vs 42 % by chance. They mark one speaker taking or yielding the floor, not agenda or topic changes.
- **Two clocks in a meeting.** Six boundary sets form two families: collective transitions (agenda stage,
  topic, reorganization event; mutual co-occurrence 1.5–1.6× chance within ±30 s) and individual floor flow
  (level shift, extended floor turn, lexical novelty peak; 1.1–1.2×). Across families the relation is null
  or negative: topic boundaries and events are rarer than chance at the onset of an extended floor turn
  (0.78–0.85×, p = .001).
- **Correction: the lexical topic boundaries are largely a turn-taking artifact.** Shuffling utterance texts
  while keeping every onset, speaker and length reproduces most of what the original TF-IDF tiling shows: its
  boundaries fall in the collaborative floor (1.65 observed vs 1.61 shuffled), coincide with events (1.62 vs
  1.52) and avoid extended floor turns (0.81 vs 0.83). Semantic segmentations (embeddings, semantic networks)
  agree with each other (1.33–1.42×), carry topic-transition markers (1.16×) and pauses, and shift most at agenda
  boundaries (d = +.27), but sit at chance in floor state and with events; continuous semantic change is larger
  when one speaker holds the floor and smaller at reorganization events (d = −.16). Coarse LLM topics (8
  meetings) align with the agenda (2.5×) and weakly with events (1.35×, p = .05). Claims about topic boundaries
  below hold for the agenda; the topic part needs semantic or human boundaries.
- **Content-only LLM topics restore the topic link.** An LLM segmentation of all 34 meetings that saw only the
  text (no speakers, no times) is the best-validated content segmentation: it agrees with the agenda (5.2×), carries
  topic-transition markers (1.91×) and pauses (1.51×), and shows a semantic jump at its boundaries (d = +.39). Its
  topic boundaries coincide with reorganization events (1.48×; 1.61× for high-confidence boundaries) and fall outside
  the singly-held floor (F1 0.53×, F2 1.47×). Text style can still reveal multi-party talk, so this is not fully
  independent of turn-taking; it is reported as qualitative corroboration, outside the turn-taking paper.
- **Agenda and topic transitions happen in the collaborative floor** (topic part: see the correction and the LLM
  result above). Classifying every 5 s as F1 (one speaker
  holds ≥ 70 % of the talk), F2 (≥ 3 active, none above 50 %) or mixed: agenda, topic and event boundaries fall in
  F2 at 1.6–1.7× chance and in F1 at 0.5–0.6×; level shifts fall in F1 (1.36×). Agenda and topic boundaries are
  independent of the turn-taking metrics. Lexical topic mixing is lowest in F1. Topics opened by an extended floor
  turn last longer (4.2 vs 2.4 min) at lower entropy than topics opened by a collective event. More centralized
  5-min blocks have fewer collective transitions (RR .86 same block, .95 next block). The end of a long turn does
  not trigger an event (1.01× chance), but its vocabulary is taken up by others above chance, more so when an event
  follows and less after the facilitator's long turns.
- **Events are bursty and refractory.** Burstiness .071 vs −.036 under a uniform null (p = 6e-8); Allan
  factor below 1 at 30–60 s and above 1 at 10 min.
- **Content mixes at events.** Lexical topic entropy is higher at events (residual d = +.35, 33/34
  meetings) and at topic boundaries (34/34), while lexical novelty relative to the previous 5 min is
  slightly *lower* (d = −.16). Reorganization recombines present content before new content appears.
  The numbers show that content changes; what changes is the question for the human-coded follow-up.
- **Robustness.** All 11 battery metrics move together at events and boundaries (PC1 = 67 %); the event
  contrast peaks at the 60-s window used throughout.
- **Not supported.** DFA does not differ from the run-shuffle null; the state-space-grid rate measures
  depend on segment length and are not interpreted.

## Files not shipped
`results/battery_windows.csv` (8 MB), `results/content_windows.csv` (4 MB) and
`results/floor_cycle_T2_states.csv` are regenerated by `battery.py`, `content.py` and `floor_cycle.py`. `content.py` reads transcript text locally; only numeric outputs are kept.

## References
Butts (2008); Costa, Goldberger & Peng (2002); Dakos et al. (2012); Goh & Barabási (2008); Gorman &
Wiltshire (2024); Hollenstein (2013); Kaspar & Schuster (1987); Lempel & Ziv (1976); Lewis, Lamey &
Douglas (1999); Peng et al. (1994); Scheffer et al. (2009); Truong, Oudre & Vayatis (2020); Wiltshire
(2026). See `references.md`.
