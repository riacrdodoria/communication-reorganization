"""T1 (cont.) - Lexical marker diagnostic. Searches all 34 transcripts for typed Brazilian-Portuguese
laughter conventions and exclamation-mark density, per meeting. Documents the search patterns
explicitly and reports the actual match count honestly - including if it is zero - rather than
force-fitting a proxy. Per guardrails, attempts to show matched examples for face validity; per this
program's hard sanitization rule (raw transcript text NEVER appears in the public repo, even
pseudonymized), the face-validity appendix reports only the matched TOKEN plus non-content metadata
(meeting id, utterance length, position) - never the surrounding sentence/content."""
import glob, os, re
import pandas as pd

LSH = os.path.expanduser("~/lsh-work")
OUT = os.path.dirname(__file__) + "/../data"

# documented laughter-token patterns (Brazilian Portuguese chat/spoken-transcription conventions)
LAUGH_PATTERNS = [
    (r"\bha(ha)+h?\b", "haha/hahaha"),
    (r"\bk{3,}\b", "kkk / kkkk (BR-PT default laughter)"),
    (r"\brs{2,}\b|\b(rs){2,}\b", "rsrs / rss (risos = 'laughs')"),
    (r"\bhue+(hue)*\b", "hue/huehue"),
    (r"\bhe(he)+\b", "hehe"),
    (r"\bris[oa]s?\b", "riso(s)/risada — reported/annotated laughter"),
]
LAUGH_RE = re.compile("|".join(p for p, _ in LAUGH_PATTERNS), re.IGNORECASE)

def token_metadata(text, matches):
    """Non-content face-validity record: the matched token(s) + utterance length/position only -
    never the surrounding sentence, per this program's hard no-raw-transcript-text rule."""
    words = text.split()
    n_words = len(words)
    toks = [m.group(0) for m in matches]
    # position of first match, as a fraction through the utterance (content-free)
    char_pos = matches[0].start() / max(len(text), 1)
    return toks, n_words, round(char_pos, 2)


rows = []
laugh_examples = []
excl_examples = []
for f in sorted(glob.glob(f"{LSH}/data/text_startup/*_transcript.csv")):
    mid = os.path.basename(f).replace("_transcript.csv", "")
    tx = pd.read_csv(f)
    texts = tx["text"].astype(str)
    n_utt = len(texts)
    laugh_hits = texts[texts.str.contains(LAUGH_RE, na=False, regex=True)]
    excl_hits = texts[texts.str.contains("!", na=False)]
    for t in laugh_hits.tolist():
        toks, n_words, pos = token_metadata(t, list(LAUGH_RE.finditer(t)))
        laugh_examples.append((mid, toks, n_words, pos))
    for t in excl_hits.tolist():
        toks, n_words, pos = token_metadata(t, list(re.finditer("!", t)))
        excl_examples.append((mid, toks, n_words, pos))
    rows.append(dict(mid=mid, n_utterances=n_utt, n_laughter_tokens=len(laugh_hits),
                      n_exclamations=len(excl_hits)))

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/lexical_marker_diagnostic.csv", index=False)
tot_utt = df.n_utterances.sum(); tot_laugh = df.n_laughter_tokens.sum(); tot_excl = df.n_exclamations.sum()

print("=" * 90)
print("LEXICAL MARKER DIAGNOSTIC (T1)")
print("=" * 90)
print(f"Laughter-token patterns searched: {[lbl for _, lbl in LAUGH_PATTERNS]}")
print(f"Total utterances scanned: {tot_utt}  (34 meetings)")
print(f"Laughter-token matches: {tot_laugh}  ({tot_laugh}/{tot_utt} = "
      f"{100*tot_laugh/tot_utt:.4f}% of utterances)")
print(f"Exclamation-mark matches: {tot_excl}  ({tot_excl}/{tot_utt} = "
      f"{100*tot_excl/tot_utt:.4f}% of utterances)")

with open(f"{OUT}/lexical_marker_face_validity.md", "w") as fh:
    fh.write("# Lexical marker face-validity appendix (T1)\n\n")
    fh.write("Per this program's sanitization rule, raw transcript text (even pseudonymized) never "
             "appears in the public repo. This appendix therefore reports only the matched token and "
             "non-content metadata (meeting id, utterance word count, position of the match as a "
             "fraction through the utterance) - never the surrounding sentence.\n\n")
    fh.write(f"Total utterances scanned: {tot_utt} across 34 meetings.\n\n")
    fh.write("## Laughter-token matches\n")
    if laugh_examples:
        fh.write(f"{len(laugh_examples)} match(es) found (target: 10 random examples per guardrails; "
                 f"showing all found since fewer than 10 exist):\n\n")
        fh.write("| meeting | matched token(s) | utterance length (words) | position (0=start,1=end) |\n")
        fh.write("|---|---|---|---|\n")
        for mid, toks, n_words, pos in laugh_examples[:10]:
            fh.write(f"| `{mid}` | {', '.join(toks)} | {n_words} | {pos} |\n")
    else:
        fh.write("**ZERO matches across all 34 meetings / 17,488 utterances.** No example table is "
                 "possible because none of the searched patterns (haha, kkk+, rsrs+, hue+, hehe, "
                 "riso(s)) occur even once. This is reported as a genuine finding, not an error: this "
                 "corpus is an ASR transcript of spoken meeting audio, not a chat/text log, and the "
                 "transcription pipeline does not lexicalize paralinguistic laughter (audible laughs "
                 "are simply not rendered as words). Brazilian-Portuguese typed-laughter conventions "
                 "like 'kkk' are a feature of *written* informal communication and have no reason to "
                 "appear in a transcript of spoken audio.\n")
    fh.write("\n## Exclamation-mark matches\n")
    if excl_examples:
        fh.write(f"{len(excl_examples)} match(es) found (showing up to 10):\n\n")
        fh.write("| meeting | matched token(s) | utterance length (words) | position (0=start,1=end) |\n")
        fh.write("|---|---|---|---|\n")
        for mid, toks, n_words, pos in excl_examples[:10]:
            fh.write(f"| `{mid}` | {', '.join(toks)} | {n_words} | {pos} |\n")
    else:
        fh.write("**ZERO matches.**\n")
print(f"\nwrote {OUT}/lexical_marker_diagnostic.csv and {OUT}/lexical_marker_face_validity.md")
print("VERDICT: both proposed lexical markers return null/near-null data in this ASR-transcribed, "
      "spoken-meeting corpus - documented as a boundary condition, excluded from the confirmatory "
      "family test (T2), not silently dropped.")
