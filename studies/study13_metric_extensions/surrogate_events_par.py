"""Parallel worker for surrogate_events.py: worker i of n handles every n-th remaining meeting; merge with --merge."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
from csd_tautology import metrics_from_state, detect, shuffled
K = 20; MAIN = f"{CM.RES}/surrogate_events.json"
if sys.argv[1] == "--merge":
    res = json.load(open(MAIN)) if os.path.exists(MAIN) else {}
    for f in [x for x in os.listdir(CM.RES) if x.startswith("surrogate_events_w")]:
        res.update(json.load(open(f"{CM.RES}/{f}"))); os.remove(f"{CM.RES}/{f}")
    json.dump(res, open(MAIN, "w")); print(len(res), "meetings"); sys.exit()
i, n = int(sys.argv[1]), int(sys.argv[2]); done = json.load(open(MAIN)) if os.path.exists(MAIN) else {}
todo = [m for m in CM.meetings() if not (m in done and len(done[m]) >= K)][i::n]; out = f"{CM.RES}/surrogate_events_w{i}.json"; res = {}
for m in todo:
    st, _ = CM.team_state(m); res[m] = []
    for _ in range(K):
        s, d, r = metrics_from_state(shuffled(st)); res[m].append(detect(s, r).tolist())
    json.dump(res, open(out, "w")); print(m, flush=True)
