"""Item 8. Routinization of who-follows-whom. Turns = maximal runs of one speaker (utterances merged). Per meeting,
a role-to-role transition matrix (facilitator and the three members of the team; self-transitions impossible by
construction). Measures: Markov entropy rate; Jensen-Shannon distance between consecutive meetings (rows weighted by
row frequency); distance of each meeting to the team's first three meetings (drift); within-meeting stationarity
(first vs second half). Trends over weeks by Kendall tau; null for the consecutive-distance trend permutes meeting
order (2000x). Output: results/routinization_meeting.csv, results/routinization_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import kendalltau
from scipy.spatial.distance import jensenshannon
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(8)

def turns(mid):
    tx = C.transcript(mid); R = C.roles(mid); r = [R.get(str(s), "OTHER") for s in tx.speaker_id]
    seq = [x for x in r if x not in ("OTHER", "BOT")]; out = []
    for x in seq:
        if not out or out[-1] != x: out.append(x)
    return out

def matrix(seq, labs):
    i = {l: k for k, l in enumerate(labs)}; M = np.zeros((len(labs), len(labs)))
    for a, b in zip(seq[:-1], seq[1:]):
        if a in i and b in i: M[i[a], i[b]] += 1
    return M

def dist(M1, M2):
    w = (M1.sum(1) + M2.sum(1)); w = w / w.sum(); d = 0
    for k in range(M1.shape[0]):
        if M1[k].sum() and M2[k].sum(): d += w[k] * jensenshannon(M1[k] / M1[k].sum(), M2[k] / M2[k].sum(), base=2)
    return d

def entropy_rate(M):
    P = M / np.maximum(M.sum(1, keepdims=True), 1); pi = M.sum(1) / M.sum(); H = 0
    for k in range(M.shape[0]):
        p = P[k][P[k] > 0]; H += pi[k] * -(p * np.log2(p)).sum()
    return H

W = C.week_map(); rows = []; mats = {}
for t in "AB":
    labs = ["FACILITATOR", f"{t}1", f"{t}2", f"{t}3"]
    ms = sorted([m for m in C.meetings() if C.team(m) == t], key=lambda m: W[m])
    for m in ms:
        s = turns(m); M = matrix(s, labs); mats[m] = M; h = len(s) // 2
        rows.append(dict(mid=m, team=t, week=W[m], n_turns=len(s), H_rate=entropy_rate(M), stationarity=dist(matrix(s[:h], labs), matrix(s[h:], labs)),
                         fac_to_member=M[0, 1:].sum() / max(1, M[0].sum()), member_to_member=M[1:, 1:].sum() / max(1, M[1:].sum())))
    base = sum(mats[m] for m in ms[:3])
    for k, m in enumerate(ms):
        rows[-len(ms) + k]["dist_prev"] = dist(mats[ms[k - 1]], mats[m]) if k else np.nan
        rows[-len(ms) + k]["dist_first3"] = dist(base, mats[m]) if k >= 3 else np.nan
T = pd.DataFrame(rows); T.to_csv(f"{C.RES}/routinization_meeting.csv", index=False); L = []
for t, g in T.groupby("team"):
    g = g.sort_values("week")
    for col in ["H_rate", "dist_prev", "dist_first3", "stationarity", "member_to_member", "fac_to_member"]:
        x = g[["week", col]].dropna(); tau, p = kendalltau(x.week, x[col])
        extra = ""
        if col == "dist_prev":
            ms = g.mid.tolist(); obs = tau; null = []
            for _ in range(2000):
                perm = rng.permutation(ms); d = [dist(mats[perm[k - 1]], mats[perm[k]]) for k in range(1, len(perm))]; null.append(kendalltau(range(len(d)), d)[0])
            extra = f" | perm-order null p={(np.sum(np.abs(null) >= abs(obs)) + 1) / 2001:.3f}; mean consecutive distance {g.dist_prev.mean():.3f}"
        L.append(f"Team {t} {col:16s} mean {g[col].mean():.3f}  trend tau={tau:+.2f} p={p:.3f}{extra}")
open(f"{C.RES}/routinization_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
