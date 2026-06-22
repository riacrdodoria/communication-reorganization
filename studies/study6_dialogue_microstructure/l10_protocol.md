# EOS Level 10 Meeting — agenda-stage segmentation protocol

These meetings follow the **Level 10 Meeting™** agenda of the Entrepreneurial Operating System (EOS;
Wickman, *Traction*, 2011). The agenda has seven canonical stages, in this order:

1. **segue** — opening check-in: greetings and one-or-two personal/business "good news" items per person;
   warm-up / small talk before business starts.
2. **scorecard** — review of the team's weekly numbers / KPIs / metrics ("scorecard"); each measure is
   on-track or off-track.
3. **rock_review** — review of the quarterly priorities ("Rocks" / quarterly goals / milestones);
   on-track or off-track.
4. **headlines** — brief customer and employee news (good/bad headlines).
5. **todo** — review of last week's to-do list / action items (done vs not done).
6. **ids** — Identify–Discuss–Solve: working through the issues list; this is the problem-solving heart of
   the meeting and is usually by far the largest block (extended discussion, debate, decisions).
7. **conclude** — wrap-up: recap of new to-dos, "cascading messages" to communicate, and **rating the
   meeting 1–10**.

## Coding instructions
- These are advisor-led ("Pulse") sessions, so stages may be **merged, reordered, shortened, or absent**.
  Mark only the stages that actually occur, in the order they occur.
- For each stage that occurs, give the **0-based utterance index where it begins** (its first utterance).
- Stages are contiguous: a stage runs until the next stage begins (or end of meeting).
- `ids` is usually the dominant block; do not split it into sub-issues here (the issue-level structure is
  captured separately by topic segmentation). Treat all the Identify–Discuss–Solve work as one `ids` stage
  (or, if the meeting clearly returns to review stages and then re-enters IDS, you may mark `ids` more than
  once — but only when the agenda genuinely re-enters problem-solving).
- Use exactly these stage names: segue, scorecard, rock_review, headlines, todo, ids, conclude.
