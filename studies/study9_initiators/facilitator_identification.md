# Facilitator identification (documented rule) — correction from "leader," then a second correction

**Terminology correction (first pass).** Earlier drafts of this study labelled this role "leader." That
is wrong: these are advisory ("Pulse"-format) meetings, and per this program's own `METHODS.md` ("Each
meeting pairs the team with the same advisor"), the person identified below is very likely **the same
external facilitator/advisor across both teams**, not each team's own internal leader. All Study 9
outputs use **"facilitator"** (external advisor) throughout; no claim is made about the team's own
internal leadership structure, which this analysis does not identify.

**Identification-method correction (second pass — this document).** The original rule identified the
facilitator by a single **constant raw `speaker_id` ("2"), applied to all 34 meetings**, chosen because
it was the *modal* (most common) opener of the `segue` and `todo` L10 stages, pooled across each team's
17 meetings (35–62% modal share — never close to 100%). That was methodologically unsound: raw
`speaker_id` in this corpus is assigned **per meeting, by order of first appearance in that specific
transcript** — it is not a persistent identity across meetings at all, so a single constant id cannot
correctly identify the same real person in more than a fraction of meetings by construction.

**Corrected rule and verification.** The facilitator's raw `speaker_id` is now resolved **per meeting**,
verified against the researcher's own retained, name-labeled source transcripts (never published; no
name appears anywhere in this repository). Verification aligned each meeting's name-labeled transcript
to its anonymized counterpart utterance-for-utterance (matching line counts confirm exact alignment) and
confirmed the facilitator's identity is **100% internally consistent within every one of the 34
meetings** (every one of his utterances maps to a single raw `speaker_id` in that meeting — no
ambiguity). The corrected per-meeting mapping is `data/facilitator_raw_id_verified.csv` (columns: `mid`,
`facilitator_raw_id`, verification counts — no names).

## Corrected distribution
The facilitator's raw `speaker_id` across the 34 meetings: **"1" in 23 meetings, "2" in 10, "3" in 1.**
The original constant ("2") was therefore the correct id in only 10/34 meetings (29%) and wrong in the
other **24/34 (71%)** — in those 24 meetings, the old pipeline was mislabeling one of the team's own
members as "facilitator" and (mechanically) mislabeling the true facilitator as a "member." This is a
correctness fix applied throughout Study 9 (event-level `facilitator` flag in `events_initiators.csv`
and everything computed from it) and propagated to Study 11's replication ledger and the manuscript.

**Why the original share-based rule (segue/todo modal speaker) undershot 100%.** With per-meeting
verification, the `segue` stage (the opening check-in) is the more reliable of the two signals: its anchor
utterance is a host-style prompt addressed to the team. The `todo` anchor is noisier: in several meetings it
captures a member's status report rather than the facilitator's own prompt, which is why `segue`-only and
`todo`-only attributions disagree within the same meeting more often than a single consistent rule would
allow. The modal-share approach therefore (correctly) reported shares well below 100 %; that should have
been read as a red flag before a constant was hardcoded.

**Corroborating (unaffected) check — to-do ownership** (Study 8 raw extraction, recomputed with the
per-meeting identification): the facilitator owns **4.7 %** (Team A) and **3.0 %** (Team B) of the to-dos
assigned in meetings — the smallest share of any participant. (Figures of 14 % / 31 % that circulated in an
earlier draft were computed with the wrong constant id.) This is the expected pattern for an external
advisory role: driving structure and assigning work to the team, not doing the team's own work.

**What this analysis does *not* establish.** It does not identify each team's own internal leader (e.g.,
a founder/CEO or informal lead among the startup's own staff). That would require a different
operationalization and is flagged as a natural follow-up, not attempted here.

**Speaker labels (2026-09-05).** Study 9 outputs no longer use per-meeting pseudonyms `S1, S2, ...`.
Every speaker is labelled by a verified, persistent ROLE (`results/speaker_roles_verified.csv`, built the
same way as the facilitator map: FACILITATOR, A1–A3, B1–B3, DEVICE; no names), so that lifts, rank
stability and the "least-talkative member" refer to persons. The earlier pseudonym scheme was a known
simplification that turned out to matter: with it, the label `S5` existed only in the eight meetings where
the transcription-tool line took an early id, which is what produced the spurious Team-A/Team-B stability
contrast reported in the first version of this study and of Study 11.
