"""Coarse topic boundaries from an earlier LLM segmentation of 8 meetings (utterance indices in validate_segmentation.py,
mapped to onsets with the original transcripts) compared with the lexical and semantic segmentations of
topic_triangulation.py, the agenda, reorganization events, extended floor turns, and floor state.
Output: results/topic_tri_llm_bounds.json, results/topic_tri_llm_summary.txt"""
import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
src = open(f"{CM.L}/validate_segmentation.py").read(); llm = eval(src[src.index("llm={") + 4:src.index("}", src.index("llm={")) + 1])
B = json.load(open(f"{CM.RES}/topic_tri_bounds.json")); P = json.load(open(f"{CM.RES}/partitions_bounds.json")); ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv")
rng = np.random.default_rng(5)
near = lambda a, b: np.min(np.abs(np.asarray(a)[:, None] - np.asarray(b)[None, :]), 1) if len(a) and len(b) else np.full(len(a), 1e9)
LB = {}
for m, idx in llm.items():
    t = pd.read_csv(f"{CM.L}/data/text_startup_with_bot/{m}_transcript.csv"); on = pd.to_numeric(t.onset_seconds, errors="coerce").ffill().to_numpy()
    LB[m] = np.array([on[min(i, len(on) - 1)] for i in idx], float)
M = list(llm)
def enrich(ref, tgt, W=30, n=500):
    obs = sum(int(np.sum(near(ref[m], tgt[m]) <= W)) for m in M)
    nul = np.array([sum(int(np.sum(near(ref[m], (np.asarray(tgt[m]) + rng.uniform(0, P[m]["T"])) % P[m]["T"]) <= W)) for m in M) for _ in range(n)])
    return obs / nul.mean(), (np.sum(nul >= obs) + 1) / (n + 1)
L = [f"LLM boundaries: {sum(len(v) for v in LB.values())} in 8 meetings; {np.mean([len(LB[m]) / (P[m]['T'] / 3600) for m in M]):.1f} per hour"]
for k in ["TILE", "EMB", "NETC", "NETG", "AGENDA"]:
    tg = {m: B[m][k] for m in M}; r, p = enrich(LB, tg); r2, p2 = enrich(tg, LB)
    L.append(f"  LLM -> {k:<6} {r:.2f} (p={p:.3f}) | {k} -> LLM {r2:.2f} (p={p2:.3f})")
for k, ref in [("event", {m: P[m]["event"] for m in M}), ("extended floor turn", {m: P[m]["floor"] for m in M})]:
    r, p = enrich(LB, ref); L.append(f"  LLM -> {k}: {r:.2f} (p enrich={p:.3f})")
obs = {"F1": 0, "MIX": 0, "F2": 0}; exp = {"F1": 0, "MIX": 0, "F2": 0}; N = 300
for m in M:
    s = ST[ST.mid == m]; sec = s.sec.to_numpy(); st = s.state.to_numpy(); bb = LB[m]
    for x in st[np.abs(sec[None, :] - bb[:, None]).argmin(1)]: obs[x] += 1
    for _ in range(N):
        sh = (bb + rng.uniform(0, P[m]["T"])) % P[m]["T"]
        for x in st[np.abs(sec[None, :] - sh[:, None]).argmin(1)]: exp[x] += 1 / N
L.append(f"  LLM boundaries by floor state (obs/expected): { {k: round(obs[k] / exp[k], 2) for k in obs} } n={sum(obs.values())}")
json.dump({m: LB[m].tolist() for m in M}, open(f"{CM.RES}/topic_tri_llm_bounds.json", "w"))
open(f"{CM.RES}/topic_tri_llm_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
