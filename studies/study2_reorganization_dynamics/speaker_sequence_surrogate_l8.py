"""
speaker_sequence_surrogate_l8.py — Gorman-faithful version (2026-09-05) of the run-order shuffle null
for the entropy<->%DET coupling. The earlier speaker_sequence_surrogate.py used the retired 1 Hz LSH
implementation (raw bits, %DET L_min=2); this one uses the exact team-state series of gorman_reimpl.py
(2 Hz bitmask states, %MaxEnt = H / n_speakers, %DET at L_min=8, 60-s window) built from the cleaned
transcripts, so the null is computed on the same metrics the paper reports.

Null: shuffle the ORDER of team-state runs (each run = maximal stretch of one bitmask state; preserves
every state's total time and the run-length distribution, destroys temporal arrangement), recompute
%MaxEnt and %DET, redetect entropy peaks (mean+2SD local maxima, 60-s separation), and recompute the
pooled r(Δentropy, Δ%DET) over ±90-s pre/post windows.

Run: ./.venv/bin/python speaker_sequence_surrogate_l8.py [N=40]
"""
from __future__ import annotations
import sys, glob, os, time
import numpy as np, pandas as pd
from scipy.stats import pearsonr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gorman_reimpl as G

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
LMIN = 8; K = 2.0; RW = 90; SEP = 60; STRIDE = 3
W = int(G.WIN_S / G.DT); HALF = W // 2; STEP = int(G.STEP_S / G.DT)

def series_from_state(state, nsp, need_det=None):
    """%MaxEnt for every 1-s window; %DET only at the window centres (seconds) in need_det (or all)."""
    nt = state.size; maxbits = np.log2(2 ** nsp)
    secs, ent = [], []
    det = {}
    for c in range(HALF, nt - HALF, STEP):
        seg = state[c - HALF:c + HALF + 1]
        _, cnt = np.unique(seg, return_counts=True); p = cnt / cnt.sum()
        s = round(c * G.DT); secs.append(s); ent.append(100.0 * (-(p * np.log2(p)).sum()) / maxbits)
        if need_det is None or s in need_det:
            det[s] = G.det_window(seg, LMIN)
    return np.array(secs), np.array(ent), det

def detect_peaks(ent):
    fin = ent[np.isfinite(ent)]; thr = fin.mean() + K * fin.std(ddof=1)
    cand = [(i, ent[i]) for i in range(1, len(ent) - 1) if np.isfinite(ent[i]) and ent[i] > thr and ent[i] >= ent[i - 1] and ent[i] >= ent[i + 1]]
    cand.sort(key=lambda x: -x[1]); kept = []
    for i, v in cand:
        if all(abs(i - x) >= SEP for x in kept): kept.append(i)
    return sorted(kept)

def pairs_from(ent, det_by_sec, secs):
    """(Δent, Δdet) per peak; det sampled every STRIDE seconds in the ±RW windows."""
    des, dds = [], []
    for p in detect_peaks(ent):
        if p - RW < 0 or p + RW >= len(ent): continue
        pre_d = [det_by_sec[secs[s]] for s in range(p - RW, p, STRIDE) if secs[s] in det_by_sec]
        post_d = [det_by_sec[secs[s]] for s in range(p + 1, p + RW + 1, STRIDE) if secs[s] in det_by_sec]
        if not pre_d or not post_d: continue
        des.append(np.nanmean(ent[p + 1:p + RW + 1]) - np.nanmean(ent[p - RW:p])); dds.append(np.mean(post_d) - np.mean(pre_d))
    return des, dds

def runs_of(state):
    idx = np.flatnonzero(np.diff(state)) + 1
    starts = np.concatenate(([0], idx)); ends = np.concatenate((idx, [state.size]))
    return [(int(state[a]), int(b - a)) for a, b in zip(starts, ends)]

def main():
    files = sorted(glob.glob("data/text_startup/*_transcript.csv"))
    states = {os.path.basename(f).replace("_transcript.csv", ""): G.build_states(pd.read_csv(f)) for f in files}
    print(f"Meetings: {len(states)}  | N_surrogate={N}, L_min={LMIN}, stride={STRIDE}", flush=True)
    # observed, from the shipped L8 metrics (identical functions)
    des, dds = [], []
    for mid in states:
        m = pd.read_csv(f"data/metrics_gorman_l8/{mid}_gorman.csv")
        secs = m.second.to_numpy(int); ent = m.entropy_g.to_numpy(float)
        d = dict(zip(secs, m.det_g.to_numpy(float)))
        a, b = pairs_from(ent, d, secs); des += a; dds += b
    r_obs = pearsonr(des, dds)[0]
    print(f"OBSERVED coupling (L8 metrics): r(Δent,Δdet) = {r_obs:.3f}  (N events={len(des)})\n", flush=True)
    rng = np.random.default_rng(42); null_r = []; t0 = time.time()
    for s in range(N):
        des, dds = [], []
        for mid, (state, nsp) in states.items():
            runs = runs_of(state); order = rng.permutation(len(runs))
            shuf = np.concatenate([np.full(runs[i][1], runs[i][0], np.int64) for i in order])
            secs, ent, _ = series_from_state(shuf, nsp, need_det=set())
            need = set()
            for p in detect_peaks(ent):
                if p - RW < 0 or p + RW >= len(ent): continue
                need.update(secs[q] for q in range(p - RW, p, STRIDE)); need.update(secs[q] for q in range(p + 1, p + RW + 1, STRIDE))
            _, _, det = series_from_state(shuf, nsp, need_det=need)
            a, b = pairs_from(ent, det, secs); des += a; dds += b
        if len(des) >= 12: null_r.append(pearsonr(des, dds)[0])
        print(f"  surrogate {s+1}/{N} done ({time.time()-t0:.0f}s; running null mean r={np.mean(null_r):.3f}, events/run~{len(des)})", flush=True)
    null_r = np.array(null_r); lo, hi = np.percentile(null_r, [2.5, 97.5])
    verdict = "BELOW null band (temporal coupling beyond the metric byproduct)" if r_obs < lo else "WITHIN null band (reproducible by shuffling run order = metric byproduct)"
    print(f"\nNULL (shuffled team-state run order, pooled, L8): mean r={null_r.mean():.3f}  95%=[{lo:.3f},{hi:.3f}]")
    print(f"OBSERVED pooled r={r_obs:.3f}  ->  {verdict}")
    pd.DataFrame(dict(null_r=null_r)).to_csv("seq_surrogate_l8_null.csv", index=False)

if __name__ == "__main__":
    main()
