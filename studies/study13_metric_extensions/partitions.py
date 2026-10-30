"""How do the different temporal partitions of a meeting relate to each other?
Six boundary sets per meeting:
  agenda   - L10 / Pulso script stage onsets (quote-anchored annotation)
  topic    - topic-episode boundaries (episode_codes.csv)
  event    - reorganization events (RMSE > mean + 2.33 SD, 8-s clustering)
  level    - %MaxEnt level shifts (PELT change points, cp_anatomy_cps.csv)
  floor    - onsets of extended floor holdings (one speaker holds >= 30 s)
  novelty  - lexical novelty peaks (residual novelty, local maxima above the meeting's 90th percentile, >= 30 s apart)
For each ordered pair (reference A, target B): pooled share of A boundaries with a B boundary within +/-W s, divided by
the share expected when B is circularly shifted within each meeting (1000 shifts, pooled across meetings); one-sided
permutation p for enrichment and for depletion. W = 30 s (15 and 60 s as sensitivity). Also boundaries per hour and median
segment length per partition. Output: results/partitions_pairs.csv, partitions_scale.csv, partitions_summary.txt,
partitions_bounds.json (boundary times per meeting, for the figure)."""
import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(91); NSH = 1000
E = C.events(); CP = pd.read_csv(f"{C.RES}/cp_anatomy_cps.csv"); CW = pd.read_csv(f"{C.RES}/content_windows.csv")

def peaks(sec, v, pct=90, sep=30):
    thr = np.nanpercentile(v, pct); idx = [i for i in range(1, len(v) - 1) if v[i] >= thr and v[i] >= v[i - 1] and v[i] >= v[i + 1]]
    idx = sorted(idx, key=lambda i: -v[i]); kept = []
    for i in idx:
        if all(abs(sec[i] - sec[k]) >= sep for k in kept): kept.append(i)
    return np.sort(sec[kept])

B = {}; T = {}
for mid in C.meetings():
    tx = C.transcript(mid); sp = tx.speaker_id.astype(str).to_numpy(); on = tx.onset_seconds.to_numpy()
    k = np.concatenate(([True], sp[1:] != sp[:-1])); ts = on[k]; dur = np.diff(np.concatenate((ts, [on.max() + 5])))
    cw = CW[CW.mid == mid].dropna(subset=["novelty_res"])
    T[mid] = float(on.max())
    B[mid] = dict(agenda=np.array([a for _, a, _ in C.stage_segments(mid)][1:], float), topic=C.episode_bounds(mid).astype(float),
                  event=E[E.mid == mid].event_onset_s.to_numpy(float), level=CP[CP.mid == mid].cp.to_numpy(float),
                  floor=ts[dur >= 30].astype(float), novelty=peaks(cw.sec.to_numpy(), cw.novelty_res.to_numpy()))
NAMES = ["agenda", "topic", "event", "level", "floor", "novelty"]

def hits(a, b, w):
    if a.size == 0 or b.size == 0: return 0
    return int((np.min(np.abs(a[:, None] - b[None, :]), 1) <= w).sum())

rows = []
for W in (15, 30, 60):
    for A in NAMES:
        for Bn in NAMES:
            if A == Bn: continue
            obs = sum(hits(B[m][A], B[m][Bn], W) for m in B); n = sum(B[m][A].size for m in B)
            null = np.zeros(NSH)
            for s in range(NSH):
                null[s] = sum(hits(B[m][A], (B[m][Bn] + rng.uniform(0, T[m])) % T[m], W) for m in B)
            rows.append(dict(W=W, ref=A, target=Bn, n_ref=n, share_obs=obs / n, share_null=null.mean() / n, ratio=obs / null.mean() if null.mean() else np.nan,
                             p_enrich=(np.sum(null >= obs) + 1) / (NSH + 1), p_deplete=(np.sum(null <= obs) + 1) / (NSH + 1)))
        print("W", W, A, flush=True)
P = pd.DataFrame(rows); P.to_csv(f"{C.RES}/partitions_pairs.csv", index=False)
sc = []
for A in NAMES:
    per_h = [B[m][A].size / (T[m] / 3600) for m in B]
    seg = np.concatenate([np.diff(np.concatenate(([0], np.sort(B[m][A]), [T[m]]))) for m in B])
    sc.append(dict(partition=A, per_hour=np.mean(per_h), median_segment_s=np.median(seg), n=sum(B[m][A].size for m in B)))
S = pd.DataFrame(sc); S.to_csv(f"{C.RES}/partitions_scale.csv", index=False)
json.dump({m: {k: v.tolist() for k, v in B[m].items()} | {"T": T[m]} for m in B}, open(f"{C.RES}/partitions_bounds.json", "w"))
L = ["Scale of each partition:", S.round(2).to_string(index=False), "",
     "Enrichment (observed / circular-shift expected share of reference boundaries with a target boundary within +/-30 s):"]
M = P[P.W == 30].pivot(index="ref", columns="target", values="ratio").loc[NAMES, NAMES]; L.append(M.round(2).to_string())
L.append(""); L.append("p (enrichment) at 30 s:"); L.append(P[P.W == 30].pivot(index="ref", columns="target", values="p_enrich").loc[NAMES, NAMES].round(3).to_string())
L.append(""); L.append("p (depletion) at 30 s:"); L.append(P[P.W == 30].pivot(index="ref", columns="target", values="p_deplete").loc[NAMES, NAMES].round(3).to_string())
for W in (15, 60):
    L.append(f"\nRatios at +/-{W} s:"); L.append(P[P.W == W].pivot(index="ref", columns="target", values="ratio").loc[NAMES, NAMES].round(2).to_string())
open(f"{C.RES}/partitions_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
