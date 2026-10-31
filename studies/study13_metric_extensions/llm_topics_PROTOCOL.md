# LLM topic segmentation protocol (content only), v1, 2026-10-30

TASK. Segment one meeting transcript into topics, from content only.

CONTEXT. Weekly advisory meetings, in Brazilian Portuguese, of an early-stage venture team with an external
advisor. The meetings loosely follow a Level 10 agenda (check-in, scorecard, rocks, headlines, to-dos, problem
solving / IDS, conclusion). You see only row numbers and utterance text. Speakers and times are hidden on purpose.
Do not open any file other than your input file, and do not look for other data.

INPUT. ~/lsh-work/data/llm_topics/input/<MID>.txt, one utterance per line: `row | text`.
Read the WHOLE file, using offset/limit until you have seen the last row.

TWO GRAINS.
1. TOPIC: a stretch of conversation about one subject or agenda item (for example one metric, one project, one
   problem, one member's update, one decision, the opening small talk). A new TOPIC starts at the first row where the
   conversation moves to a different subject. NOT a new topic: a different person continuing the same subject; a
   question, example or clarification within the subject; a brief digression (under about 5 rows) that returns.
2. SUBTOPIC: inside a topic, a shift of focus (a different aspect, sub-problem, option or next step) that stays
   within the topic's subject. The first row of a topic is never a subtopic.

RULES. A boundary is the first row of the new segment. Row 0 starts the first topic. There is no fixed number of
topics: follow the content (meetings often have roughly 5 to 20 topics, but do not force a count). Do not use who is
talking, utterance length, or back-channels ("sim", "tá", "uhum", "ok") as cues by themselves; decide from content.

LABELS. Portuguese, 2 to 6 words, no personal names and no company or product names (use generic words such as
"cliente", "produto", "investidor", "contratação").
KIND of each topic: one of procedural (agenda management, opening, closing, scheduling), report (update, status,
metrics), problem (discussion of a problem, issue or idea), decision (agreeing actions, to-dos, owners), social
(small talk), other.
CONFIDENCE of each boundary: high, medium or low.

OUTPUT. Write JSON to ~/lsh-work/data/llm_topics/out/<MID>.json exactly in this form:
{"mid": "<MID>", "n_rows": <N>, "topics": [{"start_row": 0, "label": "...", "kind": "...", "confidence": "high",
"subtopics": [{"start_row": 12, "label": "...", "confidence": "medium"}]}]}
start_row values strictly increasing; every subtopic row strictly inside its topic. Then reply only with:
done <MID> <number of topics> <number of subtopics>
