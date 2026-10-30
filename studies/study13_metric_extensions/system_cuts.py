"""Item 1c. Which cut of the meeting should carry the System I/II/III question?
Same %MaxEnt series (60-s window, 1-s step) and run-shuffle null as system_within.py, under four segmentations:
  (1) fixed windows of 5, 10, 20 min (step = half window): periodicity test, period band 60 s .. window/2.
  (2) L10 agenda stages: periodicity test only where the stage lasts >= 8 min (two cycles of a 4-min period);
  (3) topic episodes and (4) data-driven change points (PELT, L2 cost, min size 60 s, BIC-type penalty, ruptures).
Two questions per cut:
  A. Periodicity (II/III) versus fixed point (I): share of segments with p < .05 against 100 run-shuffles of the segment
     (5% expected under the null).
  B. Does the fixed point move? Between-segment share of entropy variance (eta^2) for stages and episodes, observed versus
     the same partition applied to 200 whole-meeting run-shuffles. For PELT: number of change points observed vs
     run-shuffled, and alignment of change points with stage and episode boundaries vs 1000 circular shifts.
Output: results/system_cuts_*.csv, results/system_cuts_summary.txt"""
import sys, os, numpy as np, pandas as pd, ruptures as rpt
from scipy.signal import welch
sys.path.insert(0, os.path.dirname(__file__)); import common as C
from typology import entropy_series, shuffled
rng = np.random.default_rng(51); HZ = 2; NS_P = 100; NS_ETA = 200; NCIRC = 1000

def periodic_p(seg, nsp, pmax):
    x = entropy_series(seg, nsp)
    if x.size < 2 * 60: return np.nan, np.nan
    nps = min(x.size, 256)
    def psd(y):
        y = y - np.polyval(np.polyfit(np.arange(y.size), y, 1), np.arange(y.size)); return welch(y, fs=1.0, nperseg=nps)
    f, P = psd(x); band = (f >= 1 / pmax) & (f <= 1 / 60)
    if band.sum() < 1: return np.nan, np.nan
    PS = np.array([psd(entropy_series(shuffled(seg), nsp))[1] for _ in range(NS_P)]); ref = PS.mean(0)
    stat = (P[band] / ref[band]).max(); null = (PS[:, band] / ref[band]).max(1)
    return (np.sum(null >= stat) + 1) / (NS_P + 1), 1 / f[band][np.argmax(P[band] / ref[band])]

def eta2(x, lab):
    ok = lab != "none"; x = x[ok]; lab = lab[ok]
    if len(np.unique(lab)) < 2: return np.nan
    g = pd.Series(x).groupby(lab); return (g.size() * (g.mean() - x.mean()) ** 2).sum() / ((x - x.mean()) ** 2).sum()

def labels_from_bounds(sec, bounds):
    return np.searchsorted(np.sort(bounds), sec, side="right").astype(str)

def pelt(x, pen_k=1.0):
    xs = x[::5]  # 5-s resolution for speed; min size 12 samples = 60 s
    algo = rpt.Pelt(model="l2", min_size=12, jump=1).fit(xs.reshape(-1, 1))
    pen = pen_k * np.log(xs.size) * np.var(np.diff(xs)) * 12  # BIC-type, scaled by short-range noise
    return np.array(algo.predict(pen=pen)[:-1]) * 5

def nearest(a, b):
    return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.array([])

per_rows = []; eta_rows = []; cp_rows = []
for mid in C.meetings():
    st, nsp = C.team_state(mid); T = st.size / HZ
    # (1) fixed windows
    for W in (300, 600, 1200):
        for s0 in np.arange(0, T - W + 1, W / 2):
            seg = st[int(s0 * HZ):int((s0 + W) * HZ)]
            if len(np.unique(seg)) < 2: continue
            p, per = periodic_p(seg, nsp, W / 2); per_rows.append(dict(mid=mid, cut=f"fixed_{W//60}min", unit=f"{s0:.0f}", dur_s=W, p=p, period_s=per))
    # (2) agenda stages >= 8 min
    for n, a, b in C.stage_segments(mid):
        if b - a >= 480:
            seg = st[int(a * HZ):int(b * HZ)]; p, per = periodic_p(seg, nsp, min(300, (b - a) / 2))
            per_rows.append(dict(mid=mid, cut="stage", unit=n, dur_s=b - a, p=p, period_s=per))
    # B. fixed-point location: eta^2 of stage and episode partitions, observed vs run-shuffled meeting
    x = entropy_series(st, nsp); sec = np.arange(x.size) + 30.0
    stl = C.stage_of_seconds(mid, sec); stl = np.where(stl == "pre", "none", stl).astype(object)
    epl = labels_from_bounds(sec, C.episode_bounds(mid))
    o_st, o_ep = eta2(x, stl), eta2(x, epl)
    nst, nep, ncp = [], [], []
    for k in range(NS_ETA):
        xs = entropy_series(shuffled(st), nsp); nst.append(eta2(xs, stl)); nep.append(eta2(xs, epl))
        if k < 50: ncp.append(len(pelt(xs)))
    eta_rows.append(dict(mid=mid, team=C.team(mid), eta_stage=o_st, eta_stage_null=np.mean(nst), p_stage=(np.sum(np.array(nst) >= o_st) + 1) / (NS_ETA + 1),
                         eta_episode=o_ep, eta_episode_null=np.mean(nep), p_episode=(np.sum(np.array(nep) >= o_ep) + 1) / (NS_ETA + 1)))
    # (4) PELT change points and their alignment with stage / episode boundaries
    cps = pelt(x) + 30.0; sb = np.array([a for _, a, _ in C.stage_segments(mid)][1:]); eb = C.episode_bounds(mid)
    d_st, d_ep = nearest(cps, sb).mean() if sb.size else np.nan, nearest(cps, eb).mean()
    circ_st, circ_ep = [], []
    for _ in range(NCIRC):
        sh = (cps + rng.uniform(0, T)) % T
        if sb.size: circ_st.append(nearest(sh, sb).mean())
        circ_ep.append(nearest(sh, eb).mean())
    seg_len = np.diff(np.concatenate(([0], cps, [T])))
    cp_rows.append(dict(mid=mid, team=C.team(mid), n_cp=len(cps), n_cp_null=np.mean(ncp), median_regime_min=np.median(seg_len) / 60,
                        dist_stage=d_st, dist_stage_null=np.mean(circ_st) if circ_st else np.nan, p_stage=(np.sum(np.array(circ_st) <= d_st) + 1) / (NCIRC + 1) if circ_st else np.nan,
                        dist_episode=d_ep, dist_episode_null=np.mean(circ_ep), p_episode=(np.sum(np.array(circ_ep) <= d_ep) + 1) / (NCIRC + 1)))
    r = eta_rows[-1]; c = cp_rows[-1]
    print(mid, f"eta stage {o_st:.3f}/{r['eta_stage_null']:.3f} ep {o_ep:.3f}/{r['eta_episode_null']:.3f} | cps {c['n_cp']} (null {c['n_cp_null']:.1f}) d_ep {d_ep:.0f}/{c['dist_episode_null']:.0f}s", flush=True)

P = pd.DataFrame(per_rows); EZ = pd.DataFrame(eta_rows); CP = pd.DataFrame(cp_rows)
for n, d in [("periodicity", P), ("eta", EZ), ("changepoints", CP)]: d.to_csv(f"{C.RES}/system_cuts_{n}.csv", index=False)
L = ["A. Periodicity (System II/III) by cut: share of segments with p < .05 (5% expected by chance)"]
for cut, g in P.dropna(subset=["p"]).groupby("cut"):
    L.append(f"  {cut:<12} n={len(g):>4}  periodic share {np.mean(g.p < .05):.3f}  (binomial p vs .05 = {__import__('scipy.stats', fromlist=['binomtest']).binomtest(int((g.p<.05).sum()), len(g), .05, alternative='greater').pvalue:.2f})")
L += ["", "B. Does the fixed point move? Between-segment share of %MaxEnt variance (eta^2), observed vs run-shuffled meeting",
      f"  agenda stages : {EZ.eta_stage.mean():.3f} vs {EZ.eta_stage_null.mean():.3f}; meetings p<.05: {int((EZ.p_stage<.05).sum())}/{EZ.p_stage.notna().sum()}; Wilcoxon p={C.wilcoxon_p(EZ.eta_stage-EZ.eta_stage_null)[0]:.1e}",
      f"  topic episodes: {EZ.eta_episode.mean():.3f} vs {EZ.eta_episode_null.mean():.3f}; meetings p<.05: {int((EZ.p_episode<.05).sum())}/{len(EZ)}; Wilcoxon p={C.wilcoxon_p(EZ.eta_episode-EZ.eta_episode_null)[0]:.1e}",
      "", "C. Data-driven regimes (PELT change points in %MaxEnt)",
      f"  change points per meeting {CP.n_cp.mean():.1f} vs run-shuffled {CP.n_cp_null.mean():.1f} (Wilcoxon p={C.wilcoxon_p(CP.n_cp-CP.n_cp_null)[0]:.1e}); median regime length {CP.median_regime_min.median():.1f} min",
      f"  distance to nearest stage boundary {CP.dist_stage.mean():.0f} s vs circular-shift {CP.dist_stage_null.mean():.0f} s; meetings p<.05 {int((CP.p_stage<.05).sum())}/{CP.p_stage.notna().sum()}; Wilcoxon p={C.wilcoxon_p(CP.dist_stage-CP.dist_stage_null)[0]:.1e}",
      f"  distance to nearest topic boundary {CP.dist_episode.mean():.0f} s vs circular-shift {CP.dist_episode_null.mean():.0f} s; meetings p<.05 {int((CP.p_episode<.05).sum())}/{len(CP)}; Wilcoxon p={C.wilcoxon_p(CP.dist_episode-CP.dist_episode_null)[0]:.1e}"]
open(f"{C.RES}/system_cuts_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
