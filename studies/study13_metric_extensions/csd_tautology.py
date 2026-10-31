"""Is 'variance of %DET rises before reorganization events' a tautology?
Events = onsets of clusters (8-s gap) of seconds where RMSE (method-of-analogues prediction error of the next 20 s of
%DET from earlier states with similar %DET, eps = 3) exceeds the meeting mean + 2.33 SD. Two ways the early-warning
result could be mechanical: (1) 31 % of events follow another event within 30-75 s, so the pre-event window may simply
contain the previous event, while baselines were taken far from all events; (2) conditioning on threshold crossings
of a variability-related series and looking back produces apparent early-warning signals (Boettiger & Hastings 2012).
Tests, all with the same detection rule and the same indicator (Kendall tau of rolling variance of Gaussian-detrended
%DET over [-180, -30] s, 40-s windows; 30-s gap so centred 60-s metric windows contain no post-onset data):
 (a) all events vs baselines >= 90 s from events (replication);
 (b) isolated events (no event in the previous 240 s) vs baselines that also have no event in their previous 240 s;
 (c) surrogate events: run-shuffled team-state series (same runs, random order), %DET and RMSE recomputed, events
     re-detected, the same indicator computed for surrogate events vs surrogate baselines (10 surrogates per meeting).
     The surrogate difference is what the detection procedure produces without temporal organization.
Output: results/csd_tautology.csv, results/csd_tautology_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.stats import kendalltau, wilcoxon
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
sys.path.insert(0, CM.L); import gorman_reimpl as G
from typology import shuffled
rng = np.random.default_rng(151); NSUR = 10; PRE = 150; GAP = 30; LOOK = 240
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan

def metrics_from_state(st):
    w = int(G.WIN_S / G.DT); half = w // 2
    det = np.array([G.det_window(st[c - half:c + half + 1], 8) for c in range(half, st.size - half, 2)])
    secs = np.arange(det.size) + half // 2  # 1-s steps, first centre at 30 s
    return secs, det, G.rmse_analogues(det)
def detect(secs, rmse):
    ok = ~np.isnan(rmse); thr = np.nanmean(rmse) + 2.33 * np.nanstd(rmse); hit = secs[ok & (rmse > thr)]
    if hit.size == 0: return np.array([])
    starts = [hit[0]] + [b for a, b in zip(hit[:-1], hit[1:]) if b - a > 8]; return np.array(starts, float)
def ews(secs, det, t0):
    idx = (secs >= t0 - GAP - PRE) & (secs < t0 - GAP); seg = det[idx]
    if seg.size < PRE * .9 or np.isnan(seg).mean() > .1: return np.nan
    seg = pd.Series(seg).interpolate(limit_direction="both").to_numpy(); res = seg - gaussian_filter1d(seg, 30)
    v = [res[k:k + 40].var() for k in range(0, res.size - 40 + 1, 2)]; return kendalltau(np.arange(len(v)), v)[0]
def contrast(secs, det, ev, isolated):
    T = secs.max(); start = secs.min() + GAP + PRE + (LOOK if isolated else 0)
    evs = [e for e in ev if e >= start and (not isolated or not np.any((ev < e) & (ev >= e - LOOK)))]
    pool = np.arange(start, T - 60, 5.0)
    ok = np.array([np.min(np.abs(ev - b)) >= 90 and (not isolated or not np.any((ev < b) & (ev >= b - LOOK))) for b in pool]) if ev.size else np.ones(pool.size, bool)
    pool = pool[ok]
    if not evs or pool.size < 10: return np.nan, np.nan, 0
    te = np.nanmean([ews(secs, det, e) for e in evs]); tb = np.nanmean([ews(secs, det, b) for b in rng.choice(pool, size=min(pool.size, 3 * len(evs)), replace=False)])
    return te, tb, len(evs)

if __name__ == "__main__":
    rows = []
    for m in CM.meetings():
        st, nsp = CM.team_state(m); secs, det, rmse = metrics_from_state(st); ev = detect(secs, rmse)
        r = dict(mid=m, n_events=ev.size)
        for iso in (False, True):
            te, tb, n = contrast(secs, det, ev, iso); k = "iso" if iso else "all"; r.update({f"{k}_ev": te, f"{k}_base": tb, f"{k}_n": n})
        sur = {"all": [], "iso": []}; nsev = []
        for s in range(NSUR):
            ss, sd, sr = metrics_from_state(shuffled(st)); se = detect(ss, sr); nsev.append(se.size)
            for iso in (False, True):
                te, tb, n = contrast(ss, sd, se, iso); sur["iso" if iso else "all"].append(te - tb if n else np.nan)
        r.update(sur_all=np.nanmean(sur["all"]), sur_iso=np.nanmean(sur["iso"]), sur_n_events=np.mean(nsev))
        rows.append(r); print(m, f"events {ev.size} (surrogate {np.mean(nsev):.0f}) | all {r['all_ev']-r['all_base']:+.3f} (sur {r['sur_all']:+.3f}) | isolated n={r['iso_n']} {r['iso_ev']-r['iso_base']:+.3f} (sur {r['sur_iso']:+.3f})", flush=True)
    D = pd.DataFrame(rows); D.to_csv(f"{CM.RES}/csd_tautology.csv", index=False)
    D["all_d"] = D.all_ev - D.all_base; D["iso_d"] = D.iso_ev - D.iso_base
    L = [f"Events re-detected: {D.n_events.sum()} (published 913); surrogate series yield {D.sur_n_events.mean():.1f} events per meeting vs {D.n_events.mean():.1f} observed",
         "Rise of %DET variance before events (Kendall tau, event minus baseline; meeting means):"]
    for k, lab in [("all", "all events"), ("iso", "isolated events (no event in the previous 4 min)")]:
        d = D[f"{k}_d"]; s = D[f"sur_{k}"]
        L.append(f"  {lab:<48} observed {d.mean():+.3f} (>0 in {int((d>0).sum())}/{d.notna().sum()}, p={wp(d):.1e}) | surrogate events {s.mean():+.3f} (p vs 0 {wp(s):.1e}) | observed minus surrogate {np.nanmean(d-s):+.3f} (p={wp(d-s):.1e})")
    L.append(f"  isolated events per meeting: {D.iso_n.mean():.1f}")
    open(f"{CM.RES}/csd_tautology_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
