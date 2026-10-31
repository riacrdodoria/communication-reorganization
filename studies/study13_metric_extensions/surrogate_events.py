"""Surrogate reorganization events: for every meeting, 20 run-shuffled team-state series (same runs, random order),
%DET and RMSE recomputed, events re-detected with the published rule. Times only.
Output: results/surrogate_events.json {mid: [[onsets], ...]}"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
from csd_tautology import metrics_from_state, detect, shuffled
K = 20; OUT = f"{CM.RES}/surrogate_events.json"; res = json.load(open(OUT)) if os.path.exists(OUT) else {}
for m in CM.meetings():
    if m in res and len(res[m]) >= K: continue
    st, _ = CM.team_state(m); res[m] = []
    for _ in range(K):
        s, d, r = metrics_from_state(shuffled(st)); res[m].append(detect(s, r).tolist())
    json.dump(res, open(OUT, "w")); print(m, np.mean([len(x) for x in res[m]]), flush=True)
