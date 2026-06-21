"""
speaker_sequence_surrogate.py — The decisive null for the entropy<->%DET coupling.

Question: is the peak Delta-entropy / Delta-%DET anticorrelation a real coordination
phenomenon, or a byproduct of computing two metrics from the SAME categorical speaker series?

Null: shuffle the ORDER of speaker-floor runs (preserves each speaker's total floor time
and the turn-duration distribution; destroys temporal arrangement), then RECOMPUTE entropy
and %DET from the shuffled speaker sequence, redetect peaks, recompute the coupling.
If the coupling survives -> byproduct of the metrics; if it vanishes -> real temporal coordination.

Run: ./.venv/bin/python speaker_sequence_surrogate.py [N=40]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent
TS = ROOT / "data/processed/timeseries_startup"
MET = ROOT / "data/processed/metrics_startup"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
W = 61; HALF = 30; K = 2.0; RW = 90; SEP = 60; STRIDE = 3

def state_entropy(arr):
    arr = np.asarray(arr, int)
    if arr.size == 0: return float("nan")
    _, c = np.unique(arr, return_counts=True); p = c / c.sum()
    return float(-(p * np.log2(p)).sum())

def pct_det(arr):
    arr = np.asarray(arr, int); n = arr.size
    if n < 2: return float("nan")
    eq = arr[:, None] == arr[None, :]
    total = int(np.triu(eq, 1).sum())
    if total == 0: return 0.0
    det = 0
    for off in range(1, n):
        diag = np.diagonal(eq, off).astype(int)
        if diag.sum() == 0: continue
        pad = np.concatenate(([0], diag, [0])); d = np.diff(pad)
        lens = np.where(d == -1)[0] - np.where(d == 1)[0]
        det += int(lens[lens >= 2].sum())
    return 100.0 * det / total

def entropy_series(speaker):
    n = len(speaker)
    out = np.full(n, np.nan)
    for c in range(HALF, n - HALF):
        out[c] = state_entropy(speaker[c-HALF:c+HALF+1])
    return out

def det_at(speaker, centers):
    n = len(speaker); out = {}
    for c in centers:
        if c-HALF < 0 or c+HALF+1 > n: continue
        out[c] = pct_det(speaker[c-HALF:c+HALF+1])
    return out

def detect_peaks(ent):
    fin = ent[np.isfinite(ent)]
    thr = fin.mean() + K * fin.std(ddof=1)
    cand = [(i, ent[i]) for i in range(1, len(ent)-1)
            if np.isfinite(ent[i]) and ent[i] > thr and ent[i] >= ent[i-1] and ent[i] >= ent[i+1]]
    cand.sort(key=lambda x: -x[1]); kept = []; u = []
    for i, v in cand:
        if all(abs(i - x) >= SEP for x in u): kept.append(i); u.append(i)
    return sorted(kept)

def coupling_pairs(ent, det_lookup, n):
    """Return lists of (Δentropy, Δ%DET) per peak for one (shuffled) meeting."""
    peaks = detect_peaks(ent)
    des, dds = [], []
    for p in peaks:
        if p - RW < HALF or p + RW >= n - HALF: continue
        pre_e = np.nanmean(ent[p-RW:p]); post_e = np.nanmean(ent[p+1:p+RW+1])
        pre_secs = range(p-RW, p, STRIDE); post_secs = range(p+1, p+RW+1, STRIDE)
        pre_d = [det_lookup[s] for s in pre_secs if s in det_lookup]
        post_d = [det_lookup[s] for s in post_secs if s in det_lookup]
        if not pre_d or not post_d: continue
        des.append(post_e - pre_e); dds.append(np.mean(post_d) - np.mean(pre_d))
    return des, dds

def runs_of(speaker):
    runs = []; cur = speaker[0]; ln = 1
    for v in speaker[1:]:
        if v == cur: ln += 1
        else: runs.append((cur, ln)); cur = v; ln = 1
    runs.append((cur, ln))
    return runs

def main():
    meetings = {}
    for tp in sorted(TS.glob("*_timeseries.csv")):
        mid = tp.name.replace("_timeseries.csv", "")
        sp = pd.read_csv(tp)["speaker_lsh"].to_numpy(int)
        meetings[mid] = sp
    print(f"Meetings: {len(meetings)}  | N_surrogate={N}, stride={STRIDE}")

    # ---- OBSERVED: use real metrics (same functions produced them) ----
    obs_des, obs_dds = [], []
    for mid, sp in meetings.items():
        m = pd.read_csv(MET / f"{mid}_entropy.csv").sort_values("second").drop_duplicates("second")
        sec = m["second"].to_numpy(int)
        ent = np.full(len(sp), np.nan); det = np.full(len(sp), np.nan)
        ent[sec] = m["entropy_lsh"].to_numpy(float); det[sec] = m["det_lsh"].to_numpy(float)
        peaks = detect_peaks(ent)
        for p in peaks:
            if p-RW < HALF or p+RW >= len(sp)-HALF: continue
            de = np.nanmean(ent[p+1:p+RW+1]) - np.nanmean(ent[p-RW:p])
            dd = np.nanmean(det[p+1:p+RW+1]) - np.nanmean(det[p-RW:p])
            if np.isfinite(de) and np.isfinite(dd): obs_des.append(de); obs_dds.append(dd)
    r_obs = pearsonr(obs_des, obs_dds)[0]
    print(f"OBSERVED coupling: r(Δent,Δdet) = {r_obs:.3f}  (N events={len(obs_des)})\n")

    # ---- SURROGATE: shuffle run order, recompute everything ----
    rng = np.random.default_rng(42)
    null_r = []
    for s in range(N):
        des_all, dds_all = [], []
        for mid, sp in meetings.items():
            runs = runs_of(sp)
            order = rng.permutation(len(runs))
            shuf = np.concatenate([np.full(runs[i][1], runs[i][0], int) for i in order])
            ent = entropy_series(shuf)
            peaks = detect_peaks(ent)
            need = set()
            for p in peaks:
                need.update(range(p-RW, p, STRIDE)); need.update(range(p+1, p+RW+1, STRIDE))
            det_lookup = det_at(shuf, sorted(x for x in need if 0 <= x < len(shuf)))
            de, dd = coupling_pairs(ent, det_lookup, len(shuf))
            des_all += de; dds_all += dd
        if len(des_all) >= 12:
            null_r.append(pearsonr(des_all, dds_all)[0])
        if (s+1) % 5 == 0: print(f"  surrogate {s+1}/{N} done (running null mean r={np.mean(null_r):.3f}, events/run~{len(des_all)})")
    null_r = np.array(null_r)
    lo, hi = np.percentile(null_r, [2.5, 97.5])
    verdict = "SURVIVES null (real temporal coupling)" if r_obs < lo else "WITHIN null (metric byproduct)"
    print(f"\nNULL (shuffled speaker-run order, pooled): mean r={null_r.mean():.3f}  95%=[{lo:.3f},{hi:.3f}]")
    print(f"OBSERVED pooled r={r_obs:.3f}  ->  {verdict}")
    print("\nInterpretation: if observed is below the null band, the entropy/%DET coupling")
    print("reflects real temporal organization, not just computing two metrics on one series.")

if __name__ == "__main__":
    main()
