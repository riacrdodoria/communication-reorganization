# Study 12 — Results

## Framing
The six-taxonomy content layer (Study 3) already codes socioemotional content (Bales IPA
positive/negative quadrants; act4teams-full positive/negative facets) but has never been examined as
its own layer. This study isolates it and asks whether reorganization events have a socioemotional
face — humor/warmth, tension/conflict, or neither — following the meeting-science interest in
positivity dynamics (Lehmann-Willenbrock, Allen & Kauffeld, 2013).

## T1 — Socioemotional category map
Full mapping of 45 categories (43 coded + 2 lexical) across all 6 taxonomies: `results/socioemotional_map.csv`.

**Confirmatory family (8 categories, justified individually):**
| category | scheme | valence | justification |
|---|---|---|---|
| `bsolid` (shows solidarity) | Bales IPA | + | Bales (1950) socioemotional-positive #1 |
| `btension` (tension release, jokes) | Bales IPA | + | Bales socioemotional-positive #2 — closest proxy to humor |
| `bagree` (agrees) | Bales IPA | + | Bales socioemotional-positive #3 — relational warmth, not epistemic convergence |
| `bdisagree` (disagrees) | Bales IPA | − | Bales socioemotional-negative #10 |
| `btensh` (shows tension) | Bales IPA | − | Bales socioemotional-negative #11 |
| `bantag` (shows antagonism) | Bales IPA | − | Bales socioemotional-negative #12 |
| `pos` (positive socio-emotional) | act4teams-full | + | independent facet-level coding pass (corr(A,B)=.65) |
| `neg` (negative socio-emotional) | act4teams-full | − | independent facet-level coding pass (corr(A,B)=.45) |

**Excluded, with justification** (37 categories): CACS argument-structure (5), IAM/Mercer
cognitive-epistemic (8), Bales task-area (6), act4teams-SHORT functional (9, of which `coop` and
`cprod` are affect-*adjacent* and reported separately below), ISO dialogue-act (5). Every exclusion
is tied to the scheme's own published definition, not to the result it would produce.

**Lexical markers — null result, honestly reported.** All 34 transcripts (17,488 utterances) were
searched for Brazilian-Portuguese typed-laughter conventions (haha, kkk+, rsrs+, hue+, hehe,
riso(s)/risada) and exclamation marks. Result: **1 laughter match, 1 exclamation mark, in the entire
corpus.** This is not a search failure: this corpus is an ASR transcript of spoken meeting audio, not
a chat/text log, and the transcription pipeline does not lexicalize paralinguistic laughter or reliably
preserve exclamative punctuation for spoken audio. Both markers are excluded from the confirmatory
family (no variance to test) and reported as a genuine boundary condition (`results/lexical_marker_diagnostic.csv`,
`results/lexical_marker_face_validity.md`).

## T2 — Event-locked socioemotional lift
Per-meeting density lift at RMSE reorganization events (>mean+2.33 SD) vs. baseline, Wilcoxon +
BH-FDR **within** the 8-category family:

| category | valence | mean lift | 95% CI | meetings same-dir | q (FDR) |
|---|---|---:|---|---|---|
| `bagree` | + | **+0.265** | [0.185, 0.346] | 31/34 | **<.001** |
| `pos` | + | **+0.208** | [0.104, 0.335] | 28/34 | **<.001** |
| `bsolid` | + | **+0.148** | [0.079, 0.228] | 27/34 | **<.001** |
| `btensh` | − | +0.054 | [0.017, 0.096] | 22/34 | .050 (n.s.) |
| `btension` | + | +0.047 | [0.009, 0.086] | 17/34 | .167 (n.s.) |
| `bdisagree` | − | +0.045 | [0.002, 0.089] | 22/34 | .105 (n.s.) |
| `neg` | − | +0.019 | [−0.010, 0.054] | 16/31 | .595 (n.s.) |
| `bantag`† | − | — | — | — | not tested |

† `bantag` occurs in only 10/34 meetings (too rare for the paired per-meeting test); it is retained
in the review-vs-IDS test below, where it does not depend on per-event pairing.

**Three positive categories rise significantly; zero negative categories survive FDR.** This is a
clean, one-sided result, not a weak trend among many.

**Triangulation from a third, independent coding (not re-tested, cross-referenced only).**
act4teams-SHORT's `coop` (praising/thanking/being nice) already shows a strong lift in Study 3's
original 40-category test: +0.168 (q<.0001); `cprod` (backbiting/complaining) does not (n.s., p=.458).
Per the guardrail against folding new tests back into the original family, these are reported from
the existing Study 3 result, not re-computed — and they show the identical positive-not-negative
pattern from a third, methodologically distinct coding pass.

**Event-class split (Kruskal-Wallis, window grain, BH-FDR):**
| category | TRANSITION | HANDOFF | OTHER | H | q (FDR) |
|---|---:|---:|---:|---:|---|
| `bagree` | **1.444** | 1.389 | 1.203 | 19.41 | **.0005** |
| `btension` | 0.143 | 0.111 | 0.072 | 7.05 | .118 (n.s.) |
| others | — | — | — | <4.0 | ≥.38 (n.s.) |

`bagree` is the only category surviving FDR, and it is **concentrated at topic/agenda TRANSITIONs**,
not floor handoffs (TRANSITION > HANDOFF > INTERIOR_OTHER) — the opposite of the a priori guess that
humor/warmth would lubricate interior handoffs specifically.

## T3 — Positive vs. negative asymmetry, and the review-vs-IDS contrast
**Composite asymmetry.** Per-meeting mean positive-category lift (+0.167) vs. mean negative-category
lift (+0.036): paired Wilcoxon p = **1.06e-4**, 27/34 meetings show positive > negative. The
"reorganization opens the floor smoothly, not through conflict" hypothesis is supported, not merely
consistent with the data.

**Review-vs-IDS contrast (socioemotional subset, paired Wilcoxon + BH-FDR, n=32 meetings):**
| category | valence | review − IDS | q (FDR) |
|---|---|---:|---|
| `bdisagree` | − | **−0.093** | **.022** |
| `neg` | − | **−0.032** | **.033** |
| `bantag` | − | **−0.008** | **.048** |
| `btensh` | − | +0.062 | .065 (n.s., trend opposite) |
| `bagree` | + | +0.070 | .230 (n.s.) |
| `pos` | + | +0.057 | .445 (n.s.) |
| `bsolid` | + | −0.043 | .330 (n.s.) |
| `btension` | + | −0.004 | .975 (n.s.) |

**All three categories that survive FDR are negative-valence, and all three are *higher in IDS*
(deliberation) than in the procedural review.** No positive category differs significantly by stage.
This directly answers the briefing's question: **yes, IDS is where tension lives** — disagreement,
negative affect, and antagonism concentrate in the deliberative problem-solving block, not the
procedural review; positive warmth, by contrast, is not stage-specific — it shows up at
reorganization events regardless of which stage they fall in (see T2).

## T4 — Timing within the event window
Resolution caveat (disclosed): content categories are only available at the established 90 s window
grain — coarser than the ±30 s scale used for second-resolution metrics elsewhere in this program.
"Pre/at/post" below means the window immediately before, containing, and immediately after each
event's onset, with a circular-shift null (2,000 seeded rotations, METHODS.md §6 convention).

| series | pre | at (onset) | post | at−pre (null p) | post−at (null p) |
|---|---:|---:|---:|---|---|
| positive composite | 0.868 | **0.917** | 0.867 | +0.049 (**p=.0010**) | −0.050 (**p<.0001**) |
| negative composite | 0.112 | 0.138 | 0.147 | +0.026 (**p=.0005**) | +0.008 (p=.274, n.s.) |
| `bagree` alone | 1.235 | **1.369** | 1.243 | +0.134 (**p<.0001**) | −0.126 (**p<.0001**) |
| `pos` alone | 1.176 | 1.239 | 1.190 | +0.063 (**p=.012**) | −0.049 (**p=.038**) |
| `bsolid` alone | 0.960 | 0.952 | 0.929 | −0.008 (p=.695, n.s.) | −0.023 (p=.297, n.s.) |

**The positive signature is a sharp spike coincident with the event itself** — it rises into the
onset window and falls right back out, both legs significant by circular-shift null. It is **neither
a before-the-fact lubricant (no pre-onset ramp beyond the immediate approach) nor an after-the-fact
repair** (it does not linger). `bagree` drives essentially all of this pattern; `bsolid` (solidarity),
despite its significant overall peak-vs-baseline lift in T2, shows no sharp timing signature here —
its elevation is more diffusely spread than acutely timed. The negative composite rises into the
event but, unlike the positive composite, does **not** significantly recede afterward — a different,
less symmetric temporal shape, though it never reaches significance in T2's main test.

## Honest interpretation
Reorganization events in this corpus have a genuine, one-sided socioemotional face: **agreement,
positive affect, and solidarity rise sharply and specifically at the moment of floor reorganization,
while disagreement, tension, and antagonism do not** (0/4 negative categories survive FDR in the main
test; `bantag` is too rare to even test). This is not a diffuse positivity bias — it is timed
precisely to the event (T4), concentrated specifically at topic/agenda transitions rather than
interior handoffs (T2), and it coexists with a separate, genuine finding that negative affect *does*
have a home in this corpus — the deliberative IDS stage (T3), not reorganization events themselves.
Together these results support a relational reading of Study 2's floor-opening account: **the floor
opens warmly, and where tension exists in these teams, it lives in extended problem-solving, not in
the moments the team's structure itself reorganizes.**

## Honest scope
- The confirmatory family is 8, not the originally proposed 10, categories: the 2 lexical markers
  returned null data (documented, not discarded silently) and `bantag` could not enter the main
  paired test (too rare) though it does contribute usable signal to T3's review-vs-IDS test.
- T4 operates at 90 s window grain, a genuine resolution limit relative to the ±30 s scale used for
  second-resolution metrics elsewhere in this program (e.g., Study 6's boundary analysis) — stated
  plainly, not implied to be finer than it is.
- This study reports the pooled (34-meeting) family test, consistent with Study 3's original
  approach; no per-team split was run here (unlike Study 11, which is specifically a replication
  audit).
- `coop`/`cprod` are reported by cross-reference to Study 3's already-published result, not
  re-tested, per the guardrail against folding new tests back into the original 40-category family.

## Paper paragraph (drop-in, exact statistics — likely extends Study 2/3's Results)
> Isolating the socioemotional dimension of the six-taxonomy content layer (Bales IPA
> positive/negative quadrants; act4teams-full positive/negative facets; 8-category confirmatory
> family, BH-FDR within family), reorganization events show a one-sided positive signature: agreement
> (+0.265), positive socio-emotional acts (+0.208), and solidarity (+0.148) all rise significantly at
> events (all q<.001, 27-31/34 meetings same-direction), while no negative category (disagreement,
> tension, antagonism) survives FDR. The positive-minus-negative asymmetry is itself significant
> (paired Wilcoxon p=1.06e-4, 27/34 meetings). This positive signal is a sharp spike coincident with
> the event itself — rising into the onset window and receding immediately after (both legs
> p<.02, circular-shift null, 2,000 reps) — not a before-the-fact lubricant or an after-the-fact
> repair, and it is concentrated at topic/agenda transitions rather than floor handoffs
> (Kruskal-Wallis q=.0005). Negative affect is not absent from these teams: disagreement, negative
> socio-emotional acts, and antagonism are all significantly more prevalent in the deliberative
> problem-solving stage (IDS) than in the procedural review (all q<.05) — tension has a home in this
> corpus, but it is extended problem-solving, not the moments of reorganization itself. Two
> proposed coding-free lexical markers (typed laughter conventions, exclamation density) returned
> essentially null data (1 match each across 17,488 utterances), consistent with this being an
> ASR transcript of spoken audio rather than a chat log — a disclosed boundary condition, not a
> fabricated proxy.

## Deliverables
- `src/socioemotional_map.py` → `results/socioemotional_map.csv`.
- `src/lexical_markers.py` → `results/lexical_marker_diagnostic.csv`, `results/lexical_marker_face_validity.md`.
- `src/build_socioemotional_lifts.py` → `results/socioemotional_lifts.csv`, `results/socioemotional_by_class.csv`.
- `src/socioemotional_asymmetry.py` → `results/socioemotional_pos_vs_neg.csv`, `results/socioemotional_review_vs_ids.csv`.
- `src/socioemotional_timing.py` → `results/socioemotional_timing.csv`.
- `../../paper_figures/fig_paper_S12_socioemotional.{png,pdf,svg}`.
- All data numeric; `results/lexical_marker_face_validity.md` reports the 2 lexical matches as
  matched-token + non-content metadata only (meeting id, utterance word count, position) — no
  transcript sentence content is published, per this program's hard sanitization rule.

## References
Bales, R. F. (1950). *Interaction Process Analysis*. Addison-Wesley.
Lehmann-Willenbrock, N., & Kauffeld, S. (2018). The advanced interaction analysis for teams
(act4teams) coding scheme. In *The Cambridge Handbook of Group Interaction Analysis*.
Lehmann-Willenbrock, N., Allen, J. A., & Kauffeld, S. (2013). A sequential analysis of procedural
meeting communication: how teams facilitate their meetings. *Journal of Applied Communication
Research*, 41(4), 365-388.
Klünder, J., Karras, O., Prenner, N., & Schneider, K. (2020). Do you just discuss or do you solve?
*ICSEW/SEmotion*.
Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *JRSS B*, 57(1), 289-300.
This program's Studies 2, 3, 6, 9 (event definition, content-fingerprint machinery, L10 stage
boundaries, event classification reused here).
