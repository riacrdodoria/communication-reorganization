# Study 13 — Metric extensions — results

All numbers from the scripts in this folder (2026-10-30), 34 meetings (17 per team), 913 events.
Wilcoxon tests are across meetings on within-meeting differences; permutation p = (b + 1)/(N + 1).
Run-shuffle null = the order of team-state runs is permuted (state totals and run lengths kept).

## 1. Run-shuffle check of Study 2's excursion amplitude (`runshuffle_study1.py`, 200 surrogate corpora)
| Quantity | Observed | Run-shuffle mean [95 %] | p (null ≥ obs) | Ratio |
|---|---|---|---|---|
| SD of pre-to-post entropy excursion at peaks | 14.82 | 12.94 [9.72, 16.56] | .169 | 1.15 |
| Number of entropy peaks (mean + 2 SD, 60-s separation) | 49 | 25.4 | .005 | 1.93 |
| Mean SD of the entropy series | 17.41 | 18.25 | — | 0.95 |

The amplitude that exceeded AR(1)/VAR(1) surrogates (Study 2) is reproduced by the turn-length mix. The
temporal organization lies in excursion frequency and in a slightly more regulated series.

## 2. Gorman–Wiltshire system type
**Between meetings (`typology.py`).** Periodicity (1–5 min) tested in each third of the meeting against
200 run-shuffles: 33/34 meetings System I (no periodic third), 1/34 System III (one periodic third,
period 2.4 min). Entropy SD relative to surrogates: mean ratio 0.95 (0.85–1.07).

**Within meetings, by cut (`system_within.py`, `system_cuts.py`).**
| Cut | Segments | Periodic share (p < .05) | Expected by chance |
|---|---|---|---|
| Fixed 5 min (step 2.5) | 1200 | .030 | .05 |
| Fixed 10 min (step 5) | 574 | .026 | .05 |
| Fixed 20 min (step 10) | 259 | .012 | .05 |
| L10 stage ≥ 8 min | 82 | .000 | .05 |

No cut yields periodicity above chance: within meetings the regime is System I throughout.
Periodic (II/III) and non-periodic 10-min segments do not differ in event count (+0.08, p = .84, n = 8).

**Does the fixed point move?** Share of %MaxEnt variance between segments (eta²), observed vs the same
partition applied to 200 run-shuffled versions of the meeting.
| Partition | eta² observed | eta² null | Meetings p < .05 | Wilcoxon p |
|---|---|---|---|---|
| L10 agenda stages | .097 | .055 | 11/34 | 4.3e-4 |
| Topic episodes | .368 | .281 | 15/34 | 8.8e-7 |

**Blind segmentation (PELT, L2 cost, min size 60 s).** Default penalty: 38.8 change points per meeting
vs 40.1 in run-shuffled meetings (p = .023; median regime 1.8 min). Distance to the nearest boundary vs
1000 circular shifts:
| Penalty | Change points / meeting | Stage boundary: obs vs null (s) | p | Topic boundary: obs vs null (s) | p |
|---|---|---|---|---|---|
| ×1 | 38.8 | 640 vs 633 | .52 | 76 vs 77 | .59 |
| ×5 | 10.9 | 566 vs 630 | .05 | 80 vs 77 | .33 |
| ×20 | 2.0 | 603 vs 657 | .54 | 68 vs 79 | .27 |

## 3. Critical slowing down before events (`csd.py`, `csd_gap.py`)
Pre-event window of 150 s, Gaussian detrending (bandwidth 30 s), rolling variance and lag-5
autocorrelation in 40-s windows; indicator = Kendall τ over time; 3 matched baselines per event (≥ 90 s
from any event). The metric windows are centred (60 s), so a window ending at onset contains up to 30 s
of post-onset data; the 30-s gap version is the leakage-free result.
| Gap before onset | %DET variance: meetings ev > base | p | %DET lag-5 AC: meetings ev > base | p |
|---|---|---|---|---|
| 0 s (leaks post-onset data) | 34/34 | < .0001 | 26/34 | .0005 |
| **30 s** | **32/34** | **< .0001** | **25/34** | **.0004** |
| 60 s | 23/34 | .022 | 22/34 | .041 |

With a 30-s gap, by trigger class (variance): TRANSITION 29/34 (p < .0001), INTERIOR_HANDOFF 25/34
(p = .003), INTERIOR_OTHER 24/34 (p = .025). %MaxEnt shows no variance rise at any gap.

## 4. Event rhythm (`rhythm.py`)
- Burstiness of event onsets B = .071 vs −.036 under a uniform null (Wilcoxon p = 6.2e-8; 10/34 meetings
  individually p < .05); memory M = −.047 (n.s.). Utterance onsets: B = .073, M = +.136.
- Allan factor (observed vs null): 30 s 0.88 vs 1.00 (p = 3.7e-7); 60 s 0.90 vs 1.00 (p = .001); 120 s
  1.01 vs 1.01; 300 s 1.19 vs 1.02 (p = .10); 600 s 1.28 vs 1.07 (p = .018). Events are refractory at
  30–60 s and cluster at the 10-min scale.

## 5. Routinization across weeks (`routinization.py`; Kendall τ with week, 17 meetings per team) — see §11 before using
| Measure | Team A τ (p) | Team B τ (p) |
|---|---|---|
| Markov entropy rate of speaker transitions | −.54 (.002) | −.38 (.034) |
| Member-to-member transition share | −.38 (.034) | −.59 (.001) |
| Distance to previous meeting's transition matrix | +.15 (.45) | +.10 (.63) |
| Multiscale-entropy complexity index (`multiscale.py`) | −.47 (.01) | −.12 (.54) |

## 6. Turn allocation (`rem.py`; conditional logit, 16,298 choice sets, 45,960 candidate rows) — near-event rows retracted, see §11
| Term | M1 OR (p) | Interaction with near-event (±30 s) | with IDS | with week (z) |
|---|---|---|---|---|
| Reciprocity (candidate held turn t−1) | 1.48 (1e-51) | ×0.86 (.004) | ×0.89 (.036) | ×0.95 (.065) |
| Recency (log s since last turn) | 0.61 (1e-195) | ×0.97 (.36) | ×0.89 (6e-4) | ×0.94 (7e-4) |
| Participation share so far | 11.9 (5e-87) | ×0.93 (.77) | ×4.24 (1e-8) | ×0.89 (.36) |
| Facilitator role | 1.18 (2e-10) | ×0.86 (.006) | ×1.13 (.021) | ×1.06 (.038) |

Interactions from the joint model M5 (AIC 24,108.5 vs 24,238.0 for M1; refitted 2026-10-30 with up to 3,000
BFGS iterations after one fit had not converged; changes are in the third decimal). Team-specific week trends:
reciprocity × week Team A −.018 (p = .56), Team B +.046 (p = .044); facilitator × week Team A +.045
(p = .27), Team B +.089 (p = .003).

## 7. Metric battery (`battery.py`; 60-s windows, step 5 s)
PCA on within-meeting z-scores: PC1 67 %, PC2 10 %, PC3 9 % (PC3 is silence share). Standardized
contrast d, events (±15 s vs ≥ 90 s) and topic boundaries (±15 s vs ≥ 60 s from a boundary); all
p < .0001 except silence.
| Metric | d event | d boundary | | Metric | d event | d boundary |
|---|---|---|---|---|---|---|
| %MaxEnt | +0.94 | +0.86 | | LZ76 | +0.99 | +0.79 |
| %DET | −1.13 | −0.88 | | Conditional entropy | +1.18 | +0.99 |
| RR | −0.86 | −0.80 | | Switch rate | +1.16 | +1.01 |
| LAM | −0.89 | −0.75 | | Active speakers | +0.74 | +0.75 |
| TT | −0.91 | −0.85 | | Top-speaker share | −0.69 | −0.63 |
| Silence share | +0.34 (p = .0001) | +0.19 (p = .005) | | | | |

## 8. Multiscale (`multiscale.py`)
| Window | Event d | Boundary d | Review − IDS d |
|---|---|---|---|
| 15 s | +0.74 | +0.75 | +0.11 (p = .011) |
| 30 s | +0.88 | +0.86 | +0.16 (p = .007) |
| 60 s | +0.94 | +0.86 | +0.25 (p = .001) |
| 120 s | +0.87 | +0.83 | +0.39 (p = 4e-4) |
| 240 s | +0.70 | +0.70 | +0.57 (p = 7e-5) |

DFA α of speaker switches 0.741 vs run-shuffled 0.736 (p = .12); of %MaxEnt (15 s) 1.120 vs 1.112
(p = .05). Multiscale sample entropy complexity index 11.22 vs 10.90 (p = 4.6e-4), the excess confined
to scales ≤ 22 s.

## 9. State space grid (`ssg.py`)
Axes: active speakers × top-speaker share (5 bins). The modal cell moves from "2 speakers, top share
≥ .85" at baseline and in IDS to "3 speakers, top share .40–.55" near events and in review stages
(same attractor near events and at baseline in only 2/34 meetings). Cells per 10 min and visit duration
depend on segment length (near-event and review segments are short) and are not interpreted.

## 10. Label-free content (`content.py`; TF-IDF, KMeans k ≤ 12, controls: log word counts, speakers)
| Measure | Events d (n positive) | p | Topic boundaries d (n positive) | p |
|---|---|---|---|---|
| Topic entropy (raw) | +0.69 (34/34) | 1e-10 | +0.62 (34/34) | 1e-10 |
| Topic entropy (residual) | +0.35 (33/34) | 8e-10 | +0.26 (34/34) | 1e-10 |
| Lexical novelty (raw) | −0.16 (10/34) | .005 | −0.11 (11/34) | .020 |
| Lexical novelty (residual) | −0.16 (9/34) | .001 | −0.06 (12/34) | .18 |

Lead–lag around event onset (standardized residuals): topic entropy rises from −40 s, peaks at 0 to
+10 s (+0.27), returns by +40 s; novelty is lowest at −20 s (−0.12) and turns positive after +50 s.
Cross-speaker lexical uptake .077 vs .025 for far-apart turn pairs (ratio 3.26, p = 1e-10);
self-continuation .084 (above cross-speaker, p = .003); uptake near events .078 vs baseline .075 (p = .55).
Mean novelty rises with week in Team B (τ = +.43, p = .017; Team A +.31, p = .09).

## 11. Artifact checks (`rem_artifacts.py`, `routinization_artifacts.py`)
**Turn allocation near events.** Controls: interactions of every base term with local %MaxEnt (z within meeting) and
with the number of distinct speakers in the previous 60 s. Placebo: entropy peaks above the meeting's 90th percentile
that are ≥ 90 s from any event.
| Model | reciprocity × near OR (p) | facilitator × near OR (p) |
|---|---|---|
| Near-event terms only | 0.866 (.007) | 0.862 (.006) |
| + local-entropy controls | 0.998 (.98) | 0.962 (.49) |
| Placebo peaks only | 0.851 (.065) | 0.819 (.026) |
| Circular-shift null, controlled model (100 shifts) | p = .59 | p = .27 |
Local entropy itself carries the effect (reciprocity × entropy OR .745, facilitator × entropy OR .785, both p < 1e-9).
The near-event moderation is therefore not event-specific.

**Routinization.** Decomposition: H_ind = entropy rate expected from turn shares alone; S = H_ind − H_obs.
| Kendall τ with week | Team A | Team B |
|---|---|---|
| H_obs, all meetings | −.54 (.002) | −.38 (.034) |
| H_obs, three members present | −.44 (.042) | −.47 (.016) |
| H_obs, before the transcription-tool change (weeks 1–12) | −.09 (.74) | −.52 (.021) |
| S (structure beyond shares) | +.00 (1.0) | +.38 (.034) |
| Facilitator turn share | +.37 (.042) | +.57 (.001) |
| Member-to-member excess over shares | −.12 (.54) | −.47 (.008) |
Pooled OLS with absence and tool covariates: week b = −.013 (p = .135); absence b = −.32 (p < .001); tool n.s.
Meetings with a member absent have the lowest entropy rates (0.86 vs 1.27).

## 12. Change-point anatomy (`cp_anatomy.py`; 1,318 PELT change points)
| Property | Observed | Null | p |
|---|---|---|---|
| Mean absolute level shift (%MaxEnt), vs change points of 20 run-shuffles per meeting | 26.2 | 29.3 | 3.5e-10 |
| Change points beyond the shuffle's 95th percentile | 1.7 % | 5 % | — |
| Within 15 s of a long-turn (≥ 30 s) start or end, vs circular shift | .543 | .415 | 3.6e-8 |
| Dominant floor holder differs before vs after (60 s) | .485 | .432 | 1.7e-5 |
| Mean distance to nearest event (s) | 128 | 132 | .046 |
| Strong change points (n = 22): distance to nearest event (s) | 52 | 127 | .004 |
Stage distribution of change points equals the stage distribution of meeting time (IDS 61 %). The facilitator
dominates the minute after a downward shift in 52 % of cases vs 49 % of random minutes. Content within ±15 s:
residual novelty +0.14 (p = .001), residual topic entropy −0.17 (p = 3e-5); long-turn boundaries without a change
point show the same direction (+0.18, −0.15), so the content signature belongs to extended floor turns generally.

## 13. Divisions of meeting time (`partitions.py`; 34 meetings, 1,000 circular shifts)
| Division | Boundaries | Per hour | Median segment |
|---|---|---|---|
| Agenda (Pulso / L10 stage) | 165 | 3.2 | 6.4 min |
| Topic episode | 936 | 17.9 | 2.6 min |
| Reorganization event | 913 | 17.5 | 1.8 min |
| Entropy level shift (PELT) | 1,318 | 25.4 | 1.8 min |
| Extended floor turn (≥ 30 s) | 1,543 | 29.8 | 1.6 min |
| Lexical novelty peak | 842 | 16.2 | 2.2 min |

Observed / expected share of reference boundaries with a target boundary within ±30 s (* enrichment p < .01,
° depletion p < .01):
| ref \ target | agenda | topic | event | level | floor | novelty |
|---|---|---|---|---|---|---|
| agenda | — | 1.55* | 1.49* | 1.01 | 1.02 | 1.01 |
| topic | 1.56* | — | 1.62* | 1.00 | 0.80° | 1.04 |
| event | 1.49* | 1.59* | — | 1.07 | 0.80° | 1.03 |
| level | 1.01 | 1.02 | 1.12* | — | 1.16* | 1.15* |
| floor | 0.99 | 0.78° | 0.85° | 1.19* | — | 1.09* |
| novelty | 1.09 | 1.04 | 1.03 | 1.16* | 1.14* | — |
The same two-family pattern holds at ±15 s and ±60 s (`results/partitions_summary.txt`). Figure:
`paper_figures/fig_partitions.png`.

## 14. Floor states and the two clocks (`floor_cycle.py`)
Floor state every 5 s (60-s windows): F1 = top-speaker share ≥ .70 (46 % of time); F2 = ≥ 3 active speakers and top
share < .50 (19 %); MIX otherwise (36 %). Median dwell: F1 45 s, F2 20 s, MIX 20 s.

**Boundaries by floor state** (observed / expected from 300 circular shifts; all listed ratios p < .01 except where n.s.):
| Boundary | n | F1 | MIX | F2 |
|---|---|---|---|---|
| Agenda stage | 165 | 0.58 | 1.20 | 1.58 |
| Topic | 936 | 0.59 | 1.13 | 1.63 |
| Reorganization event | 913 | 0.47 | 1.31 | 1.68 |
| Entropy level shift | 1,318 | 1.36 | 0.83 | 0.44 |
| Extended floor turn onset | 1,543 | 1.03 (n.s.) | 1.23 | 0.42 |
| Lexical novelty peak | 842 | 1.03 (n.s.) | 0.98 (n.s.) | 0.98 (n.s.) |

Content by state (mean of meeting means): residual topic entropy F1 −.025, MIX +.025, F2 +.003 (F1 vs F2 p = 3.5e-5);
residual novelty F1 +.004, F2 −.002 (p = .06).

**Long turns.** 1,543 turns ≥ 30 s; an event within [−10, +60] s of the turn end in 28.8 % (circular-shift expectation
28.4 %, ratio 1.01, p = .35; 10–30 s turns 34.9 %). Logit with meeting fixed effects: residual novelty OR .85 (p = .036),
log duration OR .76 (p = .052), facilitator OR .85 (p = .21). Lexical uptake of the long turn by other speakers in the
next 120 s exceeds a far-turn null by +.025 (p = 1.3e-8); OLS with meeting fixed effects: event follows b = +.0105
(p = .030), facilitator turn b = −.013 (p = .005), novelty n.s. Caveat: others talk more after events, which can raise
uptake. Events preceded by a long-turn end (53 % of events) do not differ in topic entropy or novelty from other events.

**Two origins of topics** (936 topics: opened by a long turn only 22.6 %, by an event only 28.7 %, both 13.2 %,
neither 35.4 %). Individual vs collective, within-meeting Wilcoxon (34 meetings): duration 4.16 vs 2.40 min (p < .001);
mean entropy 34.2 vs 48.0 %MaxEnt (p < .001); events per minute .31 vs .40 (p = .19); novelty in the first minute
.019 vs .004 (p = .07); facilitator as opener .35 vs .31 (p = .33). Review stages have more collectively opened topics
(34 %) than IDS (27 %).

**Centralization** (570 five-minute blocks, Poisson GLM with meeting fixed effects, IDS indicator): collective
boundaries (events + topics) RR .861 per SD of degree centralization in the same block (p < .001) and RR .949 in the
next block controlling for the current count (p = .048); individual boundaries (long turns + level shifts) RR 1.03
(p = .21) and 1.01 (p = .65).

**By stage** (±30 s, 500 circular shifts): topic→event 1.76 (review) and 1.47 (IDS); event→floor 0.69 and 0.78;
topic→floor 0.66 and 0.82 (all p = .002); level→floor 1.08 (n.s.) and 1.16 (p = .002); novelty→level 1.22 and 1.12
(p ≤ .012). Figure: `paper_figures/fig_partitions.png`, panel D.

## 15. Topic triangulation (`topic_triangulation.py`, `topic_llm_check.py`)
Segmentations: EMB (sentence embeddings, paraphrase-multilingual-MiniLM-L12-v2), NETC (Louvain communities of the
meeting's lemma co-occurrence network; 406 lemmas, 7.0 communities, modularity .22 on average), NETG (weighted Jaccard
between the semantic networks of the minute before and after), TILE (original lexical tiling), AGENDA, and LLM topics
(8 meetings). Time-based TextTiling depth, boundaries above mean + 0.5 SD, ≥ 60 s apart. Text-shuffle null: texts
permuted across utterances within word-count quintiles (20 per meeting).

| Segmentation | Per hour (shuffled) | Marker ±15 s (shuffled) | Pause ±15 s | F2 ratio (shuffled, 95 %) | → event (shuffled) | → floor turn (shuffled) |
|---|---|---|---|---|---|---|
| EMB | 27.3 (28.7) | 1.06 n.s. (1.00) | 1.14 | 1.00 (0.82 [0.76, 0.89]) | 1.02 n.s. (0.92) | 1.15 (1.15) |
| NETC | 27.7 (30.1) | 1.17 (1.01) | 1.13 | 1.08 (0.91 [0.86, 0.98]) | 1.06 (0.97) | 1.08 (1.11) |
| NETG | 23.5 (23.9) | 1.16 (1.04) | 1.13 | 1.03 (1.05 [0.95, 1.17]) | 1.06 (1.12) | 1.02 (1.02) |
| TILE | 17.9 (17.9) | 1.46 (1.38) | 1.44 | 1.65 (1.61 [1.55, 1.72]) | 1.62 (1.52) | 0.81 (0.83) |
| AGENDA | 3.2 | 2.37 | 1.46 | 1.63 | 1.49 | 1.03 |
| LLM (8 meetings) | 5.2 | — | — | 1.36 (F1 0.54) | 1.35 (p = .05) | 1.04 |

Agreement (±30 s): EMB–NETC 1.33, EMB–NETG 1.42, NETC–NETG 1.38, semantic–TILE 1.14–1.19, semantic–AGENDA 1.05–1.18
(n.s.), TILE–AGENDA 1.57, LLM–AGENDA 2.51, LLM–semantic 0.96–1.11 (n.s.).
Continuous semantic shift (z within meeting): at agenda boundaries EMB +.14 (p = .033), NETC +.16 (p = .012), NETG
+.27 (p = 6.5e-6); at events EMB −.16 (p = 9e-4), NETC +.05 n.s., NETG −.06 n.s.; by floor state EMB F1 +.12, MIX −.03,
F2 −.18 (F2 − F1 p = 2.5e-6), NETG F1 +.03, F2 −.07 (p = .009).
Utterance embeddings and lemmas are computed locally (`topic_semantics_cache.py`) and not distributed.

## 16. LLM topic segmentation of all 34 meetings (`llm_topics_analysis.py`, protocol `llm_topics_PROTOCOL.md`)
One agent per meeting, identical instructions, input = row number and utterance text only. 525 topic boundaries
(10.1 per hour, median topic 3.6 min) and 1,144 subtopic boundaries (22.0 per hour). Topic kinds: report 34.7 %,
problem 31.1 %, procedural 16.5 %, decision 9.8 %, social 6.6 %. Test-retest against the earlier 8-meeting LLM
segmentation: 49 % of earlier boundaries found within ±30 s (3.1× chance).

| Measure (±30 s unless noted; observed / circular expectation) | Topics | Subtopics |
|---|---|---|
| Agenda | 5.15 | 0.76 n.s. |
| Lexical tiling | 1.59 | 1.28 |
| Embeddings / semantic communities / network change | 1.27 / 1.27 / 1.18 | 1.16 / 1.07 / 1.13 |
| Topic-transition marker (±15 s) | 1.91 | 1.28 |
| Long pause (±15 s) | 1.51 | 1.25 |
| Embedding semantic shift, d (±15 s vs ≥ 60 s) | +0.39 (p = 8e-10) | +0.05 n.s. |
| Floor state F1 / MIX / F2 | 0.53 / 1.34 / 1.47 | 0.63 / 1.26 / 1.38 |
| Reorganization events | 1.48 | 1.23 |
| Extended floor turn | 1.03 n.s. | 1.05 n.s. |
All listed ratios p < .01 unless marked. By kind of the new topic, events: report 1.55, decision 1.57, procedural
1.50 (p ≤ .02), problem 1.24 (p = .06); decision and procedural topics start away from extended floor turns (0.58,
0.61; p ≤ .01). High-confidence topic boundaries 1.61× with events. Of reorganization events (mean over meetings),
24.8 % fall within ±30 s of an LLM topic boundary, 7.6 % of an agenda boundary, 25.5 % of either, and 36.5 % only of
a subtopic boundary.

