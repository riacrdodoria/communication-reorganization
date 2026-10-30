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

## 5. Routinization across weeks (`routinization.py`; Kendall τ with week, 17 meetings per team)
| Measure | Team A τ (p) | Team B τ (p) |
|---|---|---|
| Markov entropy rate of speaker transitions | −.54 (.002) | −.38 (.034) |
| Member-to-member transition share | −.38 (.034) | −.59 (.001) |
| Distance to previous meeting's transition matrix | +.15 (.45) | +.10 (.63) |
| Multiscale-entropy complexity index (`multiscale.py`) | −.47 (.01) | −.12 (.54) |

## 6. Turn allocation (`rem.py`; conditional logit, 16,298 choice sets, 45,960 candidate rows)
| Term | M1 OR (p) | Interaction with near-event (±30 s) | with IDS | with week (z) |
|---|---|---|---|---|
| Reciprocity (candidate held turn t−1) | 1.48 (1e-51) | ×0.86 (.004) | ×0.89 (.036) | ×0.95 (.065) |
| Recency (log s since last turn) | 0.61 (1e-195) | ×0.97 (.36) | ×0.89 (6e-4) | ×0.94 (7e-4) |
| Participation share so far | 11.9 (5e-87) | ×0.93 (.77) | ×4.24 (1e-8) | ×0.89 (.36) |
| Facilitator role | 1.18 (2e-10) | ×0.86 (.006) | ×1.13 (.021) | ×1.06 (.038) |

Interactions from the joint model M5 (AIC 24,108.6 vs 24,238.0 for M1). Team-specific week trends:
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
