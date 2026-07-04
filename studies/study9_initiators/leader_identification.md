# Leader/facilitator identification (documented rule)

**Rule.** Per team, the leader is the speaker who most often opens the EOS L10 `segue` (opening
check-in) and `todo` (to-do review) stages — the facilitator role in the protocol — computed from the
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
accountability review). `conclude` (closing/rating) is more evenly split and, for startup_b, actually
skews to speaker "1" — consistent with `conclude` being a group ritual (everyone states a rating) rather
than a facilitation act, so it is not used to define the leader.

**Corroborating (and nuancing) check — to-do ownership** (`data/outcomes_per_meeting.csv`-adjacent raw
extraction, Study 8): the facilitator ("2") is *not* the most common to-do **owner** in either team
(startup_a: 14%, least of the four main speakers; startup_b: 31%, second). This is the expected pattern
for an advisory/facilitator role: driving structure and assigning work, not necessarily doing the most
of it — a useful sanity check that "leader" here means *facilitator*, not *most active contributor*.

**Pseudonymization.** In all Study 9 outputs, speakers are relabelled `S1, S2, ...` per team by order of
first appearance in that meeting's transcript (not tied to the raw numeric id, which can differ in
meaning of person across meetings only by coincidence of numbering — the **leader flag** is what is
tracked consistently, not a fixed pseudonym across meetings).
