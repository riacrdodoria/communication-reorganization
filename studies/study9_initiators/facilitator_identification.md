# Facilitator identification (documented rule) — correction from "leader"

**Terminology correction.** Earlier drafts of this study labelled this role "leader." That is wrong:
these are advisory ("Pulse"-format) meetings, and per this program's own `METHODS.md` ("Each meeting
pairs the team with the same advisor"), the person identified below is very likely **the same external
facilitator/advisor across both teams**, not each team's own internal leader. All Study 9 outputs use
**"facilitator"** (external advisor) throughout; no claim is made about the team's own internal
leadership structure, which this analysis does not identify.

**Rule.** Per team, the facilitator is the speaker who most often opens the EOS L10 `segue` (opening
check-in) and `todo` (to-do review) stages — the facilitation role in the protocol — computed from the
already-extracted L10 stage-opening quotes (`data/l10_stages/*.json`) mapped to their speaker via the
transcript.

## Numbers (share of stage-openings per speaker, raw speaker_id)
| team | stage | n | modal speaker | share |
|---|---|---:|---|---:|
| startup_a | segue | 17 | 2 | 35% |
| startup_a | todo | 14 | 2 | 36% |
| startup_a | conclude | 17 | 2 | 41% |
| startup_b | segue | 17 | 2 | 47% |
| startup_b | todo | 16 | 2 | 62% |
| startup_b | conclude | 17 | 1 | 47% |

Raw speaker id **"2" is the modal facilitator of segue and todo-review in both teams** — the two
stages that most directly index who runs the meeting (opening the check-in, driving the to-do
accountability review). That the *same* raw id is modal in *both* independently-numbered teams is
itself consistent with — though not proof of — a single external advisor running both teams' Pulse
sessions, exactly as `METHODS.md` states. `conclude` (closing/rating) is more evenly split and, for
startup_b, actually skews to a different speaker ("1") — consistent with `conclude` being a group
ritual (everyone states a rating) rather than a facilitation act, so it is not used to define the
facilitator.

**Corroborating (and clarifying) check — to-do ownership** (Study 8 raw extraction): the facilitator
("2") is *not* the most common to-do **owner** in either team (startup_a: 14%, least of the four main
speakers; startup_b: 31%, second). This is exactly the expected pattern for an **external advisory
role**: driving structure and assigning work to the team, not doing the team's own work — reinforcing
that this is a facilitator, not an internal team member with delivery responsibilities.

**What this analysis does *not* establish.** It does not identify each team's own internal leader
(e.g., a founder/CEO or informal lead among the startup's own staff). That would require a different
operationalization (e.g., who is deferred to on strategic decisions, who is addressed as accountable by
teammates independent of the facilitator) and is flagged as a natural follow-up, not attempted here.

**Pseudonymization.** In all Study 9 outputs, speakers are relabelled `S1, S2, ...` per team by order of
first appearance in that meeting's transcript — the **facilitator flag** is what is tracked
consistently across meetings, not a fixed pseudonym tied to the raw numeric id.
