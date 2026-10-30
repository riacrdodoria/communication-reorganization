"""Item 4. Critical slowing down before reorganization events. For each event, the %MaxEnt and %DET series in
[-150, 0) s are detrended (Gaussian kernel, bandwidth 30 s); rolling variance and lag-5 autocorrelation in 40-s windows
are computed and their Kendall tau over time is the early-warning indicator (Dakos-style). Matched baselines: 3 random
onsets per event in the same meeting, >= 90 s from every event and >= 150 s into the meeting. Per meeting, mean tau
(events) minus mean tau (baselines); Wilcoxon across meetings. Also by trigger class.
Output: results/csd_meeting.csv, results/csd_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(4); PRE = 150; RW = 40; LAG = 5

def ews(seg):
    if np.isnan(seg).mean() > .1 or seg.size < PRE: return np.nan, np.nan
    seg = pd.Series(seg).interpolate(limit_direction="both").to_numpy()
    res = seg - gaussian_filter1d(seg, 30); v, a = [], []
    for k in range(0, seg.size - RW + 1, 2):
        w = res[k:k + RW]; v.append(w.var()); a.append(np.corrcoef(w[:-LAG], w[LAG:])[0, 1] if w.std() > 0 else np.nan)
    t = np.arange(len(v)); v = np.array(v); a = np.array(a); ok = ~np.isnan(a)
    return kendalltau(t, v)[0], (kendalltau(t[ok], a[ok])[0] if ok.sum() > 5 else np.nan)

E = C.events(); rows = []
for mid in C.meetings():
    g = C.metrics(mid).set_index("second"); sec = g.index.to_numpy(); ev = E[E.mid == mid]
    on = ev.event_onset_s.to_numpy(); ok_base = np.array([np.min(np.abs(on - s)) >= 90 for s in sec]) & (sec >= sec.min() + PRE)
    base_pool = sec[ok_base]
    for metric in ["entropy_g", "det_g"]:
        x = g[metric]
        def at(t0):
            idx = np.arange(int(t0) - PRE, int(t0)); return x.reindex(idx).to_numpy(float)
        for cls_name, sub in [("ALL", ev)] + [(c, ev[ev.event_class == c]) for c in ["TRANSITION", "INTERIOR_HANDOFF", "INTERIOR_OTHER"]]:
            te = [ews(at(t)) for t in sub.event_onset_s if t - PRE >= sec.min()]
            if not te or len(base_pool) < 10: continue
            tb = [ews(at(t)) for t in rng.choice(base_pool, size=3 * len(te), replace=True)]
            te = np.array(te, float); tb = np.array(tb, float)
            rows.append(dict(mid=mid, metric=metric, cls=cls_name, n=len(te), var_tau_ev=np.nanmean(te[:, 0]), var_tau_base=np.nanmean(tb[:, 0]),
                             ac_tau_ev=np.nanmean(te[:, 1]), ac_tau_base=np.nanmean(tb[:, 1])))
    print(mid, flush=True)
T = pd.DataFrame(rows); T.to_csv(f"{C.RES}/csd_meeting.csv", index=False); lines = []
for (m, c), g in T.groupby(["metric", "cls"]):
    dv = g.var_tau_ev - g.var_tau_base; da = g.ac_tau_ev - g.ac_tau_base
    pv, n = C.wilcoxon_p(dv); pa, _ = C.wilcoxon_p(da)
    lines.append(f"{m:9s} {c:16s} n={n:2d} variance tau ev {g.var_tau_ev.mean():+.3f} vs base {g.var_tau_base.mean():+.3f} (diff>0 in {int((dv>0).sum())}/{n}, p={pv:.4f}) | "
                 f"lag-{LAG} AC tau ev {g.ac_tau_ev.mean():+.3f} vs base {g.ac_tau_base.mean():+.3f} (diff>0 in {int((da>0).sum())}/{n}, p={pa:.4f})")
open(f"{C.RES}/csd_summary.txt", "w").write("\n".join(lines)); print("\n".join(lines))
