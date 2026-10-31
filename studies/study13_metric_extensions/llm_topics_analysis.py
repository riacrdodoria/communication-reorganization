"""Content-only LLM topic segmentation of all 34 meetings (protocol: data/llm_topics/PROTOCOL.md; one agent per meeting,
identical instructions; agents saw row numbers and text only, no speakers or times). Validation and analyses.
Boundary sets: LLMT = topic starts (row 0 excluded); LLMS = subtopic starts. Rows mapped to utterance onsets.
(1) Validity of the files; counts per hour; kinds. (2) Test-retest against the earlier 8-meeting LLM segmentation.
(3) Agreement with agenda, lexical tiling and semantic segmentations (+/-30 s vs circular shifts). (4) Independent cues
(topic-transition markers, long pauses) within +/-15 s. (5) Continuous semantic shift at LLM boundaries. (6) Floor
state (F1/MIX/F2) at boundaries. (7) Relation to reorganization events and extended floor turns, overall, by kind of the
new topic and by boundary confidence. (8) Events re-classified: within +/-30 s of an LLM topic boundary or an agenda
boundary (content transition) vs neither. (9) Two origins of LLM topics (extended floor turn vs collective event).
Labels stay local; outputs are numeric. Output: results/llm_topics_*.csv, results/llm_topics_summary.txt"""
import sys, os, json, numpy as np, pandas as pd
from collections import Counter
from scipy.stats import wilcoxon
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
rng = np.random.default_rng(121); D = f"{CM.L}/data/llm_topics/out"; CACHE = f"{CM.L}/data/semantic_cache"
P = json.load(open(f"{CM.RES}/partitions_bounds.json")); TB = json.load(open(f"{CM.RES}/topic_tri_bounds.json")); OLD = json.load(open(f"{CM.RES}/topic_tri_llm_bounds.json"))
ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv")
near = lambda a, b: np.min(np.abs(np.asarray(a)[:, None] - np.asarray(b)[None, :]), 1) if len(a) and len(b) else np.full(len(a), 1e9)
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan
L = []; bad = []; LT = {}; LS = {}; KIND = {}; CONF = {}; TOP = []
for m in CM.meetings():
    f = f"{D}/{m}.json"
    if not os.path.exists(f): bad.append((m, "missing")); continue
    j = json.load(open(f)); tx = CM.transcript(m); tx = tx[tx.text.notna()].reset_index(drop=True); on = tx.onset_seconds.to_numpy(); n = len(on)
    tops = j["topics"]; rows = [t["start_row"] for t in tops]
    if rows[0] != 0 or any(b <= a for a, b in zip(rows, rows[1:])) or rows[-1] >= n: bad.append((m, "topic rows"));
    subs = [(s["start_row"], s.get("confidence", "")) for k, t in enumerate(tops) for s in t.get("subtopics", [])]
    LT[m] = np.array([on[min(r, n - 1)] for r in rows[1:]], float); LS[m] = np.array([on[min(r, n - 1)] for r, _ in subs], float)
    KIND[m] = [t.get("kind", "other") for t in tops[1:]]; CONF[m] = [t.get("confidence", "") for t in tops[1:]]
    ends = rows[1:] + [n]
    for k, (t, e) in enumerate(zip(tops, ends)):
        TOP.append(dict(mid=m, k=k, start=on[min(t["start_row"], n - 1)], end=on[min(e, n - 1)] if e < n else on[-1] + 5, kind=t.get("kind", "other"),
                        n_sub=len(t.get("subtopics", [])), confidence=t.get("confidence", "")))
MIDS = [m for m in CM.meetings() if m in LT]; Tm = {m: P[m]["T"] for m in MIDS}
L.append(f"(1) files: {len(MIDS)}/34 valid; problems: {bad}")
TT = pd.DataFrame(TOP); TT["dur_min"] = (TT.end - TT.start) / 60; TT.to_csv(f"{CM.RES}/llm_topics_topics.csv", index=False)
L.append(f"    topics per hour {np.mean([len(LT[m]) / (Tm[m] / 3600) for m in MIDS]):.1f}; subtopics per hour {np.mean([len(LS[m]) / (Tm[m] / 3600) for m in MIDS]):.1f}; median topic {TT.dur_min.median():.1f} min")
L.append("    kinds (share of topics): " + TT.kind.value_counts(normalize=True).round(3).to_dict().__str__())

def enrich(ref, tgt, W=30, n=300, mids=None):
    mids = mids or MIDS
    obs = sum(int(np.sum(near(ref[m], tgt[m]) <= W)) for m in mids); tot = sum(len(ref[m]) for m in mids)
    nul = np.array([sum(int(np.sum(near(ref[m], (np.asarray(tgt[m]) + rng.uniform(0, Tm[m])) % Tm[m]) <= W)) for m in mids if len(tgt[m])) for _ in range(n)])
    return (obs / nul.mean() if nul.mean() else np.nan), (np.sum(nul >= obs) + 1) / (n + 1), (np.sum(nul <= obs) + 1) / (n + 1), tot

# (2) test-retest
om = [m for m in OLD if m in LT]
if om:
    r, p, _, n = enrich({m: np.array(OLD[m]) for m in om}, LT, mids=om); r2, p2, _, n2 = enrich(LT, {m: np.array(OLD[m]) for m in om}, mids=om)
    hit = sum(int(np.sum(near(OLD[m], LT[m]) <= 30)) for m in om) / sum(len(OLD[m]) for m in om); hit2 = sum(int(np.sum(near(LT[m], OLD[m]) <= 30)) for m in om) / sum(len(LT[m]) for m in om)
    L.append(f"(2) test-retest vs earlier LLM (8 meetings): old found in new {hit:.2f} (ratio {r:.2f}, p={p:.3f}); new found in old {hit2:.2f} (ratio {r2:.2f}, p={p2:.3f}); n old {n}, new {n2}")

# (3) agreement
L.append("(3) agreement (+/-30 s, observed / circular; * p < .01)")
others = {"AGENDA": {m: np.array(P[m]["agenda"]) for m in MIDS}, "TILE": {m: np.array(TB[m]["TILE"]) for m in MIDS}, "EMB": {m: np.array(TB[m]["EMB"]) for m in MIDS},
          "NETC": {m: np.array(TB[m]["NETC"]) for m in MIDS}, "NETG": {m: np.array(TB[m]["NETG"]) for m in MIDS}}
rows = []
for a, A in [("LLMT", LT), ("LLMS", LS)]:
    for b, B in others.items():
        r, p, _, _ = enrich(A, B); r2, p2, _, _ = enrich(B, A); rows.append(dict(llm=a, other=b, llm_to_other=r, p=p, other_to_llm=r2, p2=p2))
        L.append(f"    {a} -> {b:<6} {r:.2f}{'*' if p < .01 else ''} | {b} -> {a} {r2:.2f}{'*' if p2 < .01 else ''}")
pd.DataFrame(rows).to_csv(f"{CM.RES}/llm_topics_agreement.csv", index=False)

# (4) cues
cues = {}; pauses = {}
for m in MIDS:
    z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); on = z["onset"]; nw = z["nw"]
    end_prev = np.concatenate(([-np.inf], np.minimum(on[:-1] + .5 * nw[:-1], on[1:]))); gap = np.clip(on - end_prev, 0, None); gap[0] = 0
    cues[m] = on[z["cue"]]; pauses[m] = on[gap >= np.percentile(gap[1:], 75)]
L.append("(4) independent cues within +/-15 s (observed / circular)")
for a, A in [("LLMT", LT), ("LLMS", LS)]:
    r1, p1, _, _ = enrich(A, cues, W=15); r2, p2, _, _ = enrich(A, pauses, W=15)
    L.append(f"    {a}: topic-transition marker {r1:.2f} (p={p1:.3f}) | long pause {r2:.2f} (p={p2:.3f})")

# (5) continuous semantic shift at LLM boundaries (recomputed EMB/NETG curves are not cached: use embeddings directly)
def emb_shift(m):
    z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); on = z["onset"]; E = z["emb"].astype(float) * np.maximum(z["nw"], 1)[:, None]
    grid = np.arange(60, Tm[m] - 60, 5.0); cs = np.vstack([np.zeros((1, E.shape[1])), np.cumsum(E, 0)])
    a = np.searchsorted(on, grid - 60); mm = np.searchsorted(on, grid); b = np.searchsorted(on, grid + 60); Lb = cs[mm] - cs[a]; Rb = cs[b] - cs[mm]
    nl = np.linalg.norm(Lb, axis=1); nr = np.linalg.norm(Rb, axis=1); s = np.where((nl > 0) & (nr > 0), (Lb * Rb).sum(1) / np.maximum(nl * nr, 1e-12), np.nan)
    x = 1 - s; return grid, (x - np.nanmean(x)) / np.nanstd(x)
rows = []
for m in MIDS:
    g, zx = emb_shift(m); r = dict(mid=m)
    for a, A in [("LLMT", LT), ("LLMS", LS)]:
        d = near(g, A[m]) if len(A[m]) else np.full(g.size, 1e9); r[a] = np.nanmean(zx[d <= 15]) - np.nanmean(zx[d >= 60])
    rows.append(r)
S5 = pd.DataFrame(rows)
L.append(f"(5) embedding semantic shift at LLM topic boundaries d={S5.LLMT.mean():+.3f} (p={wp(S5.LLMT):.1e}); at subtopic boundaries d={S5.LLMS.mean():+.3f} (p={wp(S5.LLMS):.1e})")

# (6) floor state
def state_ratio(bset, n=100):
    obs = Counter(); exp = Counter()
    for m in MIDS:
        s = ST[ST.mid == m]; secs = s.sec.to_numpy(); stt = s.state.to_numpy(); bb = np.asarray(bset[m])
        if bb.size == 0: continue
        obs.update(stt[np.abs(secs[None, :] - bb[:, None]).argmin(1)])
        for _ in range(n):
            sh = (bb + rng.uniform(0, Tm[m])) % Tm[m]; exp.update(stt[np.abs(secs[None, :] - sh[:, None]).argmin(1)])
    return {k: (obs[k] / (exp[k] / n) if exp[k] else np.nan) for k in ("F1", "MIX", "F2")}, sum(obs.values())
L.append("(6) floor state at boundaries (observed / circular)")
for a, A in [("LLMT", LT), ("LLMS", LS)]:
    r, n = state_ratio(A); L.append(f"    {a} n={n}: F1 {r['F1']:.2f}  MIX {r['MIX']:.2f}  F2 {r['F2']:.2f}")
for kd in ["report", "problem", "decision", "procedural", "social"]:
    sub = {m: LT[m][np.array([k == kd for k in KIND[m]], bool)] if len(LT[m]) else LT[m] for m in MIDS}
    if sum(len(v) for v in sub.values()) >= 20:
        r, n = state_ratio(sub, n=60); L.append(f"    LLMT starting a '{kd}' topic n={n}: F1 {r['F1']:.2f}  MIX {r['MIX']:.2f}  F2 {r['F2']:.2f}")

# (7) events and extended floor turns
EV = {m: np.array(P[m]["event"]) for m in MIDS}; FL = {m: np.array(P[m]["floor"]) for m in MIDS}
L.append("(7) relation to reorganization events and extended floor turns (+/-30 s)")
rows = []
for a, A in [("LLMT", LT), ("LLMS", LS)]:
    r, p, _, n = enrich(A, EV); rf, _, pdf, _ = enrich(A, FL); rows.append(dict(set=a, n=n, event=r, event_p=p, floor=rf, floor_p_deplete=pdf))
    L.append(f"    {a} n={n}: -> event {r:.2f} (p={p:.3f}) | -> extended floor turn {rf:.2f} (p depletion={pdf:.3f})")
for kd in ["report", "problem", "decision", "procedural", "social"]:
    sub = {m: LT[m][np.array([k == kd for k in KIND[m]], bool)] if len(LT[m]) else LT[m] for m in MIDS}
    if sum(len(v) for v in sub.values()) >= 20:
        r, p, _, n = enrich(sub, EV); rf, _, pdf, _ = enrich(sub, FL); rows.append(dict(set=f"LLMT_{kd}", n=n, event=r, event_p=p, floor=rf, floor_p_deplete=pdf))
        L.append(f"    LLMT '{kd}' n={n}: -> event {r:.2f} (p={p:.3f}) | -> floor turn {rf:.2f} (p dep={pdf:.3f})")
for cf in ["high", "medium", "low"]:
    sub = {m: LT[m][np.array([c == cf for c in CONF[m]], bool)] if len(LT[m]) else LT[m] for m in MIDS}
    if sum(len(v) for v in sub.values()) >= 20:
        r, p, _, n = enrich(sub, EV); rows.append(dict(set=f"LLMT_conf_{cf}", n=n, event=r, event_p=p)); L.append(f"    LLMT confidence {cf} n={n}: -> event {r:.2f} (p={p:.3f})")
pd.DataFrame(rows).to_csv(f"{CM.RES}/llm_topics_relations.csv", index=False)

# (8) events re-classified by content transition
rows = []
for m in MIDS:
    ev = EV[m]; ag = np.array(P[m]["agenda"])
    if ev.size == 0: continue
    near_l = near(ev, LT[m]) <= 30 if len(LT[m]) else np.zeros(ev.size, bool); near_a = near(ev, ag) <= 30 if ag.size else np.zeros(ev.size, bool)
    near_s = near(ev, LS[m]) <= 30 if len(LS[m]) else np.zeros(ev.size, bool)
    rows.append(dict(mid=m, n=ev.size, topic=near_l.mean(), agenda=near_a.mean(), topic_or_agenda=(near_l | near_a).mean(), subtopic_only=(near_s & ~near_l & ~near_a).mean()))
E8 = pd.DataFrame(rows); E8.to_csv(f"{CM.RES}/llm_topics_event_classes.csv", index=False)
L.append(f"(8) events within +/-30 s of an LLM topic boundary {E8.topic.mean():.3f}, of an agenda boundary {E8.agenda.mean():.3f}, of either {E8.topic_or_agenda.mean():.3f}; of a subtopic boundary only {E8.subtopic_only.mean():.3f} (mean over meetings)")

# (9) two origins of LLM topics
TT = TT[TT.k > 0].copy(); TT["ind"] = [near([s], FL[m])[0] <= 30 for s, m in zip(TT.start, TT.mid)]; TT["col"] = [near([s], EV[m])[0] <= 30 for s, m in zip(TT.start, TT.mid)]
TT["origin"] = np.where(TT.ind & TT.col, "both", np.where(TT.ind, "individual", np.where(TT.col, "collective", "neither")))
g = TT.groupby(["mid", "origin"]).dur_min.mean().unstack()
L.append("(9) LLM topics by origin: share " + TT.origin.value_counts(normalize=True).round(3).to_dict().__str__() + "; median duration (min) " + TT.groupby("origin").dur_min.median().round(2).to_dict().__str__()
         + f"; individual vs collective within meeting p={wp(g.get('individual') - g.get('collective')):.3f}")
L.append("    origin by kind (row shares): " + pd.crosstab(TT.kind, TT.origin, normalize="index").round(2).to_string().replace("\n", " | "))
TT.drop(columns=[]).to_csv(f"{CM.RES}/llm_topics_topics.csv", index=False)
json.dump({m: {"topic": LT[m].tolist(), "subtopic": LS[m].tolist()} for m in MIDS}, open(f"{CM.RES}/llm_topics_bounds.json", "w"))
open(f"{CM.RES}/llm_topics_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
