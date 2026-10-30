#!/usr/bin/env python3
"""Convergent validity of the Last-Speaker-Holds (LSH) representation on Gorman et al. (2020) archival
teams (surgical and submarine), recomputed with the Paper 1 parameters:
  2 Hz grid, 60-s window, 1-s step, %DET with L_min = 8 (L_min = 2 also reported), RMSE by the method of
  analogues (eps = 3 %DET, horizon 20 s), events = RMSE > within-session mean + 2.33 SD, 8-s clustering.

Input: per-second canonical series data/processed/canonical/<team>.csv (second, speaker_id; 0 = silence),
built by pipeline/00_ingest.py from the archival spreadsheets. Standard = speaker_id with 0 as its own state;
LSH = last non-zero speaker carried forward.

Outputs (study1_lsh_validation/results/): lsh_convergent_team.csv (per team r for entropy, %DET, RMSE,
event overlap), lsh_convergent_summary.csv (per domain), lsh_convergent_panel.csv (one minute of both
series plus entropy for the figure), and a console summary.
"""
import sys, os, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import pearsonr
sys.path.insert(0, os.path.expanduser("~/lsh-work"))
from gorman_reimpl import rmse_analogues  # same RMSE function as the corpus metrics

def det_fast(seg, lmins=(8, 2)):
    """%DET for a categorical window: recurrent points on diagonals of length >= lmin, as a percentage of
    all recurrent points (upper triangle). Vectorized equivalent of gorman_reimpl.det_window."""
    n = seg.size; tot_rec = 0; counted = {l: 0 for l in lmins}
    for off in range(1, n):
        d = seg[:n - off] == seg[off:]
        if not d.any(): continue
        tot_rec += int(d.sum())
        pad = np.concatenate(([False], d, [False])); edges = np.flatnonzero(pad[1:] != pad[:-1])
        runs = edges[1::2] - edges[0::2]
        for l in lmins: counted[l] += int(runs[runs >= l].sum())
    if tot_rec == 0: return {l: 0.0 for l in lmins}
    return {l: 100.0 * counted[l] / tot_rec for l in lmins}

HZ = 2; DT = 1 / HZ; WIN_S = 60; STEP_S = 1; LMIN = 8; EVENT_Z = 2.33; GAP_S = 8
CAN = Path(os.path.expanduser("~/lsh-work/data/processed/canonical"))
OUT = Path(os.path.expanduser("~/lsh-work/study1_lsh_validation/results")); OUT.mkdir(parents=True, exist_ok=True)

def lsh(series):
    out = []; last = 0
    for v in series:
        if v > 0: last = v
        out.append(last)
    return np.array(out)

def metrics(state_1hz, n_states_max):
    state = np.repeat(state_1hz, HZ)  # 1 Hz archival epochs to the 2 Hz grid
    nt = state.size; w = int(WIN_S / DT); half = w // 2; step = int(STEP_S / DT)
    maxbits = np.log2(n_states_max)
    secs, ent, det8, det2 = [], [], [], []
    for c in range(half, nt - half, step):
        seg = state[c - half:c + half + 1]
        _, cnt = np.unique(seg, return_counts=True); p = cnt / cnt.sum()
        H = -(p * np.log2(p)).sum(); d = det_fast(seg)
        secs.append(round(c * DT)); ent.append(100 * H / maxbits); det8.append(d[8]); det2.append(d[2])
    det8 = np.array(det8); rm = rmse_analogues(det8)
    return pd.DataFrame({"second": secs, "entropy": ent, "det": det8, "det2": det2, "rmse": rm})

def events(rmse):
    x = np.asarray(rmse, float); ok = ~np.isnan(x)
    if ok.sum() < 10: return []
    thr = np.nanmean(x) + EVENT_Z * np.nanstd(x); idx = np.where(ok & (x > thr))[0]
    if idx.size == 0: return []
    ev = []; start = idx[0]; prev = idx[0]
    for i in idx[1:]:
        if i - prev > GAP_S: ev.append((start, prev)); start = i
        prev = i
    ev.append((start, prev)); return ev

def overlap(ev_a, ev_b, tol=GAP_S):
    if not ev_a or not ev_b: return np.nan, np.nan
    hit_a = sum(any(not (a1 + tol < b0 or b1 + tol < a0) for b0, b1 in ev_b) for a0, a1 in ev_a)
    hit_b = sum(any(not (b1 + tol < a0 or a1 + tol < b0) for a0, a1 in ev_a) for b0, b1 in ev_b)
    return hit_a / len(ev_a), hit_b / len(ev_b)

def r(a, b):
    m = ~(np.isnan(a) | np.isnan(b))
    return pearsonr(a[m], b[m])[0] if m.sum() > 3 else np.nan

inv = pd.read_csv(CAN / "inventory.csv"); inv = inv[inv.status.astype(str).eq("processed")]
rows = []; panel_done = False
for row in inv.itertuples(index=False):
    tid = str(row.team_id); df = pd.read_csv(CAN / f"{tid}.csv")
    std = pd.to_numeric(df.speaker_id, errors="coerce").fillna(0).astype(int).to_numpy()
    nsp = len(set(std[std > 0]))
    ls = lsh(std)
    # drop leading silence before the first speaker (identical in both representations after that)
    first = np.argmax(std > 0); std = std[first:]; ls = ls[first:]
    ms = metrics(std, nsp + 1); ml = metrics(ls, nsp)
    ea, eb = events(ms.rmse.to_numpy()), events(ml.rmse.to_numpy()); oa, ob = overlap(ea, eb)
    rows.append(dict(team_id=tid, domain=row.domain, n_speakers=nsp, seconds=len(std), silence_pct=100 * (std == 0).mean(),
                     r_entropy=r(ms.entropy.to_numpy(), ml.entropy.to_numpy()), r_det_l8=r(ms.det.to_numpy(), ml.det.to_numpy()),
                     r_det_l2=r(ms.det2.to_numpy(), ml.det2.to_numpy()), r_rmse=r(ms.rmse.to_numpy(), ml.rmse.to_numpy()),
                     mean_entropy_std=ms.entropy.mean(), mean_entropy_lsh=ml.entropy.mean(), mean_det_std=ms.det.mean(), mean_det_lsh=ml.det.mean(),
                     mean_rmse_std=np.nanmean(ms.rmse), mean_rmse_lsh=np.nanmean(ml.rmse),
                     n_events_std=len(ea), n_events_lsh=len(eb), events_std_matched=oa, events_lsh_matched=ob))
    print(f"{tid:26s} {row.domain:10s} nsp={nsp} sec={len(std):5d} sil={100*(std==0).mean():4.1f}%  r_ent={rows[-1]['r_entropy']:.3f} r_det8={rows[-1]['r_det_l8']:.3f} r_det2={rows[-1]['r_det_l2']:.3f} r_rmse={rows[-1]['r_rmse']:.3f}  events {len(ea)}/{len(eb)} matched {oa if oa==oa else float('nan'):.2f}/{ob if ob==ob else float('nan'):.2f}", flush=True)
    if not panel_done and row.domain == "surgical" and len(std) > 600 and (std == 0).mean() > 0.15:
        # one-minute excerpt around the first LSH entropy peak after the first 5 minutes
        e = ml.entropy.to_numpy(); s = ml.second.to_numpy(); k = np.argmax(np.where(s > 300, e, -1)); c = int(s[k])
        a, b = max(0, c - 30), c + 30
        pd.DataFrame({"second": np.arange(a, b), "speaker_standard": std[a:b], "speaker_lsh": ls[a:b]}).to_csv(OUT / "lsh_convergent_panel_series.csv", index=False)
        pd.DataFrame({"second": ms.second, "entropy_standard": ms.entropy, "entropy_lsh": ml.entropy, "det_standard": ms.det, "det_lsh": ml.det}).to_csv(OUT / f"lsh_convergent_panel_metrics_{tid}.csv", index=False)
        panel_done = True

T = pd.DataFrame(rows); T.to_csv(OUT / "lsh_convergent_team.csv", index=False)
summ = []
for dom, g in list(T.groupby("domain")) + [("all", T)]:
    d = dict(domain=dom, n_teams=len(g))
    for m in ["r_entropy", "r_det_l8", "r_det_l2", "r_rmse", "events_std_matched", "events_lsh_matched"]:
        d[f"{m}_mean"] = g[m].mean(); d[f"{m}_min"] = g[m].min(); d[f"{m}_max"] = g[m].max()
    for m in ["entropy", "det", "rmse"]:
        d[f"between_r_{m}"] = pearsonr(g[f"mean_{m}_std"], g[f"mean_{m}_lsh"])[0] if len(g) > 3 else np.nan
    summ.append(d)
S = pd.DataFrame(summ); S.to_csv(OUT / "lsh_convergent_summary.csv", index=False)
print("\nSUMMARY"); print(S.round(3).to_string(index=False))
