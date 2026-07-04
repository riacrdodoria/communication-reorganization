"""T1c - Map every extracted quote to a timestamp (substring search, the same robust method used for
L10 stage boundaries: 0/34 unmappable quotes there), verify it really is a substring, and aggregate the
per-meeting raw extractions (annotations/raw/*.json) plus the cross-meeting to-do completion pairs
(annotations/pairs/*.json) into the publishable numeric outcomes_per_meeting.csv. Also writes a QA
summary (extraction coverage, n unmappable, spot-check sample) to annotations/qa_summary.json and
study8_outcomes/QA_SUMMARY.md (no verbatim quotes in the published QA doc)."""
import glob, os, json, re, unicodedata, random
import numpy as np, pandas as pd

LSH = os.path.expanduser("~/lsh-work")
BASE = os.path.expanduser("~/lsh-work/study8_outcomes")
TXT = f"{LSH}/data/text_startup"
RAW = f"{BASE}/annotations/raw"
PAIRS = f"{BASE}/annotations/pairs"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def load_transcript(mid):
    tx = pd.read_csv(f"{TXT}/{mid}_transcript.csv")
    tx["norm"] = tx["text"].apply(norm)
    return tx


def map_quote(tx, quote, start=0):
    """Return (utterance_idx, onset_seconds) for the first row (from `start` on, else anywhere)
    whose normalized text contains the normalized quote as a substring. None if unmappable."""
    if not quote:
        return None, None, False
    q = norm(quote)[:80]
    if not q:
        return None, None, False
    for i in range(start, len(tx)):
        if q in tx.norm.iloc[i]:
            return i, float(tx.onset_seconds.iloc[i]), True
    for i in range(0, len(tx)):
        if q in tx.norm.iloc[i]:
            return i, float(tx.onset_seconds.iloc[i]), True
    return None, None, False


def parse_date_team(mid):
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})(startup_[ab])", mid)
    y, mo, d, team = m.groups()
    return int(f"{y}{mo}{d}"), team


qa_rows = []
spot_pool = []
outcome_rows = []

raw_files = sorted(glob.glob(f"{RAW}/*.json"))
print(f"found {len(raw_files)} raw extraction files")

for f in raw_files:
    mid = os.path.basename(f).replace(".json", "")
    d = json.load(open(f))
    tx = load_transcript(mid)
    date, team = parse_date_team(mid)

    # --- ratings ---
    rvals = []
    for r in d.get("ratings", []):
        idx, sec, ok = map_quote(tx, r.get("quote", ""))
        qa_rows.append(dict(mid=mid, kind="rating", mapped=ok))
        if ok and isinstance(r.get("value"), (int, float)) and 0 <= r["value"] <= 10:
            rvals.append(r["value"])
            spot_pool.append(dict(mid=mid, kind="rating", value=r["value"], mapped=ok, sec=sec))

    # --- todos assigned ---
    todos = d.get("todos_assigned", [])
    for t in todos:
        idx, sec, ok = map_quote(tx, t.get("quote", ""))
        qa_rows.append(dict(mid=mid, kind="todo_assigned", mapped=ok))
        spot_pool.append(dict(mid=mid, kind="todo_assigned", desc=t.get("description", ""), mapped=ok, sec=sec))

    # --- IDS issues ---
    issues = d.get("ids_issues", [])
    n_resolved = 0
    for it in issues:
        idx, sec, ok = map_quote(tx, it.get("quote_raised", ""))
        qa_rows.append(dict(mid=mid, kind="issue_raised", mapped=ok))
        resolved = bool(it.get("resolved_in_meeting"))
        if resolved:
            qr = it.get("quote_resolution")
            _, _, ok2 = map_quote(tx, qr) if qr else (None, None, False)
            qa_rows.append(dict(mid=mid, kind="issue_resolution", mapped=ok2))
            if ok2:
                n_resolved += 1
        spot_pool.append(dict(mid=mid, kind="issue", desc=it.get("description", ""), resolved=resolved, mapped=ok))

    outcome_rows.append(dict(
        mid=mid, team=team, date=date,
        rating_found=bool(d.get("rating_found")),
        rating_n=len(rvals),
        rating_mean=float(np.mean(rvals)) if rvals else np.nan,
        rating_min=float(np.min(rvals)) if rvals else np.nan,
        rating_max=float(np.max(rvals)) if rvals else np.nan,
        n_todos_assigned=len(todos),
        n_issues_raised=len(issues),
        n_issues_resolved_same_meeting=n_resolved,
        issue_resolution_rate_same_meeting=(100 * n_resolved / len(issues)) if issues else np.nan,
    ))

O = pd.DataFrame(outcome_rows).sort_values(["team", "date"])
O["week"] = O.groupby("team").cumcount()

# --- fold in cross-meeting to-do completion (T1b pairs) ---
pair_files = sorted(glob.glob(f"{PAIRS}/*.json"))
print(f"found {len(pair_files)} to-do completion pair files")
comp_rows = []
for f in pair_files:
    d = json.load(open(f))
    mid_t = d["mid_t"]
    tx_t1 = load_transcript(d["mid_t1"])
    statuses = d.get("todo_status", [])
    n = len(statuses)
    n_done = sum(1 for s in statuses if s.get("status") == "done")
    n_partial = sum(1 for s in statuses if s.get("status") == "partial")
    n_not = sum(1 for s in statuses if s.get("status") == "not_done")
    n_unm = sum(1 for s in statuses if s.get("status") == "unmentioned")
    for s in statuses:
        q = s.get("quote")
        ok = True
        if q:
            _, _, ok = map_quote(tx_t1, q)
        qa_rows.append(dict(mid=d["mid_t1"], kind="todo_status", mapped=ok))
    tracked = n_done + n_partial + n_not  # unmentioned excluded from the rate denominator (see RESULTS.md)
    rate = 100 * (n_done + 0.5 * n_partial) / tracked if tracked else np.nan
    comp_rows.append(dict(mid=mid_t, n_todos_tracked=n, n_todos_done=n_done, n_todos_partial=n_partial,
                           n_todos_not_done=n_not, n_todos_unmentioned=n_unm,
                           todo_completion_rate=rate))
C = pd.DataFrame(comp_rows)
O = O.merge(C, on="mid", how="left")

os.makedirs(f"{BASE}/data", exist_ok=True)
O.to_csv(f"{BASE}/data/outcomes_per_meeting.csv", index=False)
print(f"\nwrote {BASE}/data/outcomes_per_meeting.csv  ({len(O)} meetings)")

# --- QA summary (numeric only, no quotes) ---
QA = pd.DataFrame(qa_rows)
qa_summary = {
    "n_datums_extracted": int(len(QA)),
    "n_mapped": int(QA.mapped.sum()),
    "n_unmappable": int((~QA.mapped).sum()),
    "mapped_rate_pct": round(100 * QA.mapped.mean(), 1),
    "by_kind": QA.groupby("kind").mapped.agg(["count", "sum"]).rename(columns={"sum": "mapped"}).assign(
        rate_pct=lambda x: round(100 * x.mapped / x["count"], 1)).reset_index().to_dict("records"),
    "meetings_with_rating": int(O.rating_found.sum()),
    "meetings_total": int(len(O)),
    "rating_coverage_pct": round(100 * O.rating_found.mean(), 1),
}
json.dump(qa_summary, open(f"{BASE}/annotations/qa_summary.json", "w"), indent=1)

random.seed(0)
spot = random.sample(spot_pool, min(15, len(spot_pool)))
lines = ["# Study 8 extraction QA summary\n",
         f"- Datums extracted: **{qa_summary['n_datums_extracted']}**",
         f"- Quote-mapped to a timestamp: **{qa_summary['n_mapped']}** ({qa_summary['mapped_rate_pct']}%)",
         f"- Unmappable: **{qa_summary['n_unmappable']}**",
         f"- Meetings with a spoken rating: **{qa_summary['meetings_with_rating']}/{qa_summary['meetings_total']}** "
         f"({qa_summary['rating_coverage_pct']}%)\n",
         "## By datum kind\n", "| kind | n | mapped | rate |", "|---|---:|---:|---:|"]
for r in qa_summary["by_kind"]:
    lines.append(f"| {r['kind']} | {r['count']} | {r['mapped']} | {r['rate_pct']}% |")
lines += ["\n## Spot-check sample (n=15 random extracted items, mapping status only — no verbatim quotes here)\n",
          "| mid | kind | mapped | note |", "|---|---|---|---|"]
for s in spot:
    note = s.get("desc", "") or (f"value={s.get('value')}" if "value" in s else "")
    if "resolved" in s:
        note = f"resolved={s['resolved']}"
    lines.append(f"| {s['mid']} | {s['kind']} | {s['mapped']} | {note} |")
open(f"{BASE}/QA_SUMMARY.md", "w").write("\n".join(lines))
print(f"wrote {BASE}/QA_SUMMARY.md")
print(json.dumps(qa_summary, indent=1)[:800])
