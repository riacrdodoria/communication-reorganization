"""Check of Study 1's 'supra-autoregressive' claim against a stricter null: shuffle the order of team-state runs
(keeps every state's total time and the run-length distribution; destroys temporal arrangement), recompute %MaxEnt
with the same 60-s window, redetect entropy peaks with the Study 1 rule (mean + 2 SD local maxima, 60-s separation),
and recompute (a) the pooled SD of the pre-to-post entropy excursion (+/-90 s), (b) the number of peaks, (c) the SD
of the entropy series. 200 surrogate corpora. Output: results/runshuffle_study1.csv and a summary line."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as C
from typology import entropy_series, shuffled  # same window and shuffle
rng = np.random.default_rng(21); NS = 200; K, Wd, SEP = 2.0, 90, 60

def peaks_excursions(ent):
    thr = ent.mean() + K * ent.std(ddof=1); cand = [(i, ent[i]) for i in range(1, ent.size - 1) if ent[i] > thr and ent[i] >= ent[i - 1] and ent[i] >= ent[i + 1]]
    cand.sort(key=lambda x: -x[1]); kept = []
    for i, v in cand:
        if all(abs(i - x) >= SEP for x in kept): kept.append(i)
    return [ent[i + 1:i + Wd + 1].mean() - ent[i - Wd:i].mean() for i in kept if i - Wd >= 0 and i + Wd < ent.size]

S = {mid: C.team_state(mid) for mid in C.meetings()}
obs_d = []; obs_sd = []
for mid, (st, n) in S.items():
    e = entropy_series(st, n); obs_d += peaks_excursions(e); obs_sd.append(e.std())
rows = [dict(kind="observed", sd_excursion=np.std(obs_d, ddof=1), n_peaks=len(obs_d), mean_series_sd=np.mean(obs_sd))]
for k in range(NS):
    d = []; sds = []
    for mid, (st, n) in S.items():
        e = entropy_series(shuffled(st), n); d += peaks_excursions(e); sds.append(e.std())
    rows.append(dict(kind="null", sd_excursion=np.std(d, ddof=1), n_peaks=len(d), mean_series_sd=np.mean(sds)))
    if k % 20 == 0: print(k, rows[-1], flush=True)
T = pd.DataFrame(rows); T.to_csv(f"{C.RES}/runshuffle_study1.csv", index=False); o = T.iloc[0]; nl = T.iloc[1:]
for c in ["sd_excursion", "n_peaks", "mean_series_sd"]:
    lo, hi = np.percentile(nl[c], [2.5, 97.5]); p = (np.sum(nl[c] >= o[c]) + 1) / (NS + 1)
    print(f"{c}: observed {o[c]:.2f} | run-shuffle null mean {nl[c].mean():.2f} [{lo:.2f}, {hi:.2f}] | one-sided p(null >= obs) = {p:.3f} | ratio {o[c]/nl[c].mean():.2f}")
