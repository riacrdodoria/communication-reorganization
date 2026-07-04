# Study 8 outcome-extraction protocol

Companion to `l10_protocol.md` (EOS Level 10 agenda). These meetings ritually produce three outcome
signals inside the transcript itself. All three are extracted **quote-anchored**: every datum carries a
verbatim substring of the transcript (never a paraphrase) so it can be mapped back to a timestamp by
substring search (the same robust method used for L10 stage boundaries — index-based mapping was tried
first and was unreliable on long transcripts; quote-based mapping had 0/34 unmappable quotes).

## 1. Meeting rating (in `conclude`)
Near the end of the meeting the facilitator asks each participant "nota de 0 a 10, quanto vocês dão para
essa reunião?" (rate the meeting 0-10) and **each participant states their own number aloud**, often with
a short justification. Extract **one entry per spoken rating** (not one per meeting) — a meeting can have
2-5 individual ratings. If no rating ritual occurs, mark `found: false` and say so.

## 2. To-dos assigned
New commitments/action items a participant takes on ("eu vou fazer X até quinta", "fico responsável por
Y"). These appear mainly in the `todo` review, `ids`, and `conclude` ("cascading messages") stages, but can
appear anywhere. Extract each as a short paraphrase-free description **with the owner's speaker_id** and
the verbatim quote where the commitment is made.

## 3. To-do completion (cross-meeting, done in a second pass)
The `todo` stage of the *next* meeting reviews whether last meeting's commitments happened. A second
annotator is given last meeting's to-do list and this meeting's transcript, and classifies each item:
`done` / `partial` / `not_done` / `unmentioned` (not brought up at all), with a quote if mentioned.

## 4. IDS issues raised / resolved
The `ids` stage (Identify-Discuss-Solve) works through the issues list. Extract each distinct issue raised
(a short description + quote) and whether the *same meeting* closes it with an explicit decision/solution
(quote), or leaves it open.

## Anti-hallucination rules
- Every quote must be an exact contiguous substring of some utterance's `text` field (copy-paste, do not
  retype from memory).
- If unsure whether something counts (e.g., a vague aspiration vs a real commitment), do not force it —
  omit it rather than invent structure.
- Do not infer numbers not spoken aloud. A rating must be an explicit number 0-10 spoken by a person about
  the meeting itself.
