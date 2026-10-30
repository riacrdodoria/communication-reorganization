#!/usr/bin/env python3
"""Corpus check: standard multi-speaker state series (silence = state 0, overlaps allowed, offsets = onset +
0.5 s per word) versus the same series with the last non-empty state carried forward through silence (LSH),
for all 34 meetings, with the Paper 1 parameters (2 Hz, 60-s window, L_min = 8, RMSE eps 3 / h 20, events =
RMSE > mean + 2.33 SD, 8-s clustering). The standard series is exactly what data/metrics_gorman_l8 holds.
Writes study1_lsh_validation/results/corpus_lsh_vs_standard.csv and a summary line."""
import os, sys, glob, numpy as np, pandas as pd
from scipy.stats import pearsonr
sys.path.insert(0, os.path.expanduser("~/lsh-work"))
import gorman_reimpl as G
from importlib import util
spec = util.spec_from_file_location("ar", os.path.expanduser("~/lsh-work/study1_lsh_validation/lsh_convergent_current_params.py"))
src = open(spec.origin).read().split("inv = pd.read_csv")[0]; ns = {}; exec(src, ns)
det_fast, events, overlap, rr = ns["det_fast"], ns["events"], ns["overlap"], ns["r"]

def metrics(state, nsp):
    w = int(G.WIN_S / G.DT); half = w // 2; step = int(G.STEP_S / G.DT); maxbits = np.log2(2 ** nsp)
    ent, det = [], []
    for c in range(half, state.size - half, step):
        seg = state[c - half:c + half + 1]
        _, cnt = np.unique(seg, return_counts=True); p = cnt / cnt.sum()
        ent.append(100 * (-(p * np.log2(p)).sum()) / maxbits); det.append(det_fast(seg, (8,))[8])
    det = np.array(det); return np.array(ent), det, G.rmse_analogues(det)

rows = []
for f in sorted(glob.glob(os.path.expanduser("~/lsh-work/data/text_startup/*_transcript.csv"))):
    mid = os.path.basename(f).replace("_transcript.csv", "")
    df = pd.read_csv(f); state, nsp = G.build_states(df)
    ls = state.copy(); last = 0
    for i in range(ls.size):
        if ls[i] == 0: ls[i] = last
        else: last = ls[i]
    es, ds, rs = metrics(state, nsp); el, dl, rl = metrics(ls, nsp)
    ea, eb = events(rs), events(rl); oa, ob = overlap(ea, eb)
    rows.append(dict(mid=mid, n_speakers=nsp, silence_frac=(state == 0).mean(), overlap_frac=np.mean([bin(int(s)).count("1") > 1 for s in state]),
                     r_entropy=rr(es, el), r_det=rr(ds, dl), r_rmse=rr(rs, rl), n_events_std=len(ea), n_events_lsh=len(eb),
                     events_std_matched=oa, events_lsh_matched=ob, mean_ent_std=es.mean(), mean_ent_lsh=el.mean(), mean_det_std=ds.mean(), mean_det_lsh=dl.mean()))
    print(f"{mid}: sil={rows[-1]['silence_frac']:.3f} r_ent={rows[-1]['r_entropy']:.3f} r_det={rows[-1]['r_det']:.3f} r_rmse={rows[-1]['r_rmse']:.3f} events {len(ea)}/{len(eb)} matched {oa:.2f}/{ob:.2f}", flush=True)
T = pd.DataFrame(rows); out = os.path.expanduser("~/lsh-work/study1_lsh_validation/results/corpus_lsh_vs_standard.csv"); T.to_csv(out, index=False)
print("\nSUMMARY (34 meetings): median r entropy %.3f  det %.3f  rmse %.3f | events matched std %.2f lsh %.2f | silence frac mean %.3f | between-meeting r entropy %.3f det %.3f" % (
    T.r_entropy.median(), T.r_det.median(), T.r_rmse.median(), T.events_std_matched.mean(), T.events_lsh_matched.mean(), T.silence_frac.mean(),
    pearsonr(T.mean_ent_std, T.mean_ent_lsh)[0], pearsonr(T.mean_det_std, T.mean_det_lsh)[0]))
