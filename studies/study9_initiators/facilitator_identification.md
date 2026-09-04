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

**Why the original share-based rule (segue/todo modal speaker) undershot 100%.** With the benefit of
per-meeting verification, `segue` alone (the opening check-in prompt) is the more reliable of the two
signals — its anchor quotes read as generic host-style prompts ("any more news from you to share")
addressed to the team, consistent with a facilitation act. `todo`'s anchor quote is noisier: in several
meetings it captures a team member's status report rather than the facilitator's own prompt, which is
why `segue`-only and `todo`-only speaker attributions disagree within the same meeting more often than
expected under a single consistent rule. This is documented here as the reason the original modal-share
approach (correctly) reported shares well below 100% instead of treating that as a red flag before
hardcoding a constant.

**Corroborating (unaffected) check — to-do ownership** (Study 8 raw extraction): the facilitator is not
the most common to-do **owner** in either team's corrected data. This is exactly the expected pattern for
an **external advisory role**: driving structure and assigning work to the team, not doing the team's
own work.

**What this analysis does *not* establish.** It does not identify each team's own internal leader (e.g.,
a founder/CEO or informal lead among the startup's own staff). That would require a different
operationalization and is flagged as a natural follow-up, not attempted here.

**Pseudonymization.** In all Study 9 outputs, speakers are relabelled `S1, S2, ...` per team **per
meeting** by order of first appearance in that meeting's transcript — the **facilitator flag** is what
is tracked consistently across meetings (via the corrected per-meeting raw-id lookup), not a fixed
pseudonym tied to the raw numeric id, and not a claim that "S1"/"S2"/etc. refer to the same real person
across different meetings for the *other* (non-facilitator) team members either — that remains a known
simplification of the per-meeting pseudonymization scheme, unrelated to the facilitator correction here.
