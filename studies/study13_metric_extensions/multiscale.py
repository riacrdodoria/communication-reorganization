"""Item 2. Multiscale structure of the turn-taking series.
(a) Window sweep: %MaxEnt with windows W = 15, 30, 60, 120, 240 s; at each W, standardized event contrast (+/-15 s of
    event onsets vs >= 90 s away), topic-boundary contrast (+/-15 s vs >= 60 s away), and review-vs-IDS difference.
(b) DFA scaling exponent (alpha, scales 8-512 s) of the 1-Hz speaker-switch series and of %MaxEnt at W = 15 s,
    against run-shuffled surrogates (20 per meeting).
(c) Multiscale sample entropy (m = 2, r = 0.2 SD) of the 1-Hz speaker-switch count series, coarse-grained at
    scales 1-30 s, observed versus run-shuffled.
Trends over weeks for alpha and the MSE complexity index. Output: results/multiscale_*.csv, multiscale_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(__file__)); import common as C
from typology import shuffled
rng = np.random.default_rng(41); HZ = 2; WS = [15, 30, 60, 120, 240]; NSUR = 20

def ent_series(state, nsp, wsec):
    win = int(wsec * HZ) + 1; vals = np.unique(state); cs = {v: np.concatenate(([0], np.cumsum(state == v))) for v in vals}
    centers = np.arange(win // 2, state.size - win // 2, HZ); a = centers - win // 2; b = a + win; H = np.zeros(centers.size)
    for v in vals:
        p = (cs[v][b] - cs[v][a]) / win; nz = p > 0; H[nz] -= p[nz] * np.log2(p[nz])
    return centers / HZ, 100 * H / nsp

def switch_1hz(state):
    ch = np.concatenate(([0], (np.diff(state) != 0).astype(int))); n = ch.size // HZ * HZ; return ch[:n].reshape(-1, HZ).sum(1)

def dfa(x, scales=(8, 16, 32, 64, 128, 256, 512)):
    y = np.cumsum(x - x.mean()); F = []; S = []
    for s in scales:
        n = y.size // s
        if n < 4: continue
        seg = y[:n * s].reshape(n, s); t = np.arange(s); res = []
        for r in seg: res.append(np.sqrt(np.mean((r - np.polyval(np.polyfit(t, r, 1), t)) ** 2)))
        F.append(np.mean(res)); S.append(s)
    return np.polyfit(np.log(S), np.log(F), 1)[0]

def sampen(x, m=2, rf=.2):
    x = np.asarray(x, float); n = x.size; r = rf * x.std()
    if n < 50 or r == 0: return np.nan
    def count(mm):
        X = np.lib.stride_tricks.sliding_window_view(x, mm)[: n - m]; c = 0
        for i in range(len(X) - 1): c += np.sum(np.max(np.abs(X[i + 1:] - X[i]), 1) <= r)
        return c
    B = count(m); A = count(m + 1); return -np.log(A / B) if A > 0 and B > 0 else np.nan

def mse(x, scales=range(1, 31, 3)):
    return [sampen(x[: x.size // s * s].reshape(-1, s).mean(1)) for s in scales]

E = C.events(); Wk = C.week_map(); sweep = []; frac = []; ms_rows = []
for mid in C.meetings():
    st, nsp = C.team_state(mid); ev = E[E.mid == mid].event_onset_s.to_numpy(); bd = C.episode_bounds(mid)
    for w in WS:
        sec, e = ent_series(st, nsp, w); de = np.min(np.abs(ev[:, None] - sec[None, :]), 0); db = np.min(np.abs(bd[:, None] - sec[None, :]), 0)
        sd = e.std(); stg = C.stage_of_seconds(mid, sec)
        rev = e[np.isin(stg, list(C.REVIEW))]; ids = e[stg == "ids"]
        sweep.append(dict(mid=mid, W=w, d_event=(e[de <= 15].mean() - e[de >= 90].mean()) / sd, d_bound=(e[db <= 15].mean() - e[db >= 60].mean()) / sd,
                          d_review_ids=(rev.mean() - ids.mean()) / sd if rev.size > 30 and ids.size > 30 else np.nan, sd=sd))
    sw = switch_1hz(st); _, e15 = ent_series(st, nsp, 15)
    a_sw = dfa(sw.astype(float)); a_e = dfa(e15)
    nul = [(dfa(switch_1hz(s).astype(float)), dfa(ent_series(s, nsp, 15)[1])) for s in (shuffled(st) for _ in range(NSUR))]
    frac.append(dict(mid=mid, team=C.team(mid), week=Wk[mid], alpha_switch=a_sw, alpha_switch_null=np.mean([n[0] for n in nul]), alpha_ent15=a_e, alpha_ent15_null=np.mean([n[1] for n in nul])))
    m_obs = mse(sw.astype(float)); m_nul = np.nanmean([mse(switch_1hz(shuffled(st)).astype(float)) for _ in range(5)], 0)
    ms_rows.append(dict(mid=mid, team=C.team(mid), week=Wk[mid], **{f"se_{s}": v for s, v in zip(range(1, 31, 3), m_obs)}, **{f"null_{s}": v for s, v in zip(range(1, 31, 3), m_nul)},
                        CI=np.nansum(m_obs), CI_null=np.nansum(m_nul)))
    print(mid, f"alpha switch {a_sw:.2f} (null {frac[-1]['alpha_switch_null']:.2f}) ent15 {a_e:.2f} (null {frac[-1]['alpha_ent15_null']:.2f}) CI {np.nansum(m_obs):.2f} (null {np.nansum(m_nul):.2f})", flush=True)
S = pd.DataFrame(sweep); F = pd.DataFrame(frac); M = pd.DataFrame(ms_rows)
for n, d in [("sweep", S), ("fractal", F), ("mse", M)]: d.to_csv(f"{C.RES}/multiscale_{n}.csv", index=False)
L = ["(a) Window sweep: mean standardized contrast across meetings (Wilcoxon p)"]
for w, g in S.groupby("W"):
    L.append(f"  W={w:>3}s  event {g.d_event.mean():+.2f} (p={C.wilcoxon_p(g.d_event)[0]:.1e})  boundary {g.d_bound.mean():+.2f} (p={C.wilcoxon_p(g.d_bound)[0]:.1e})  review-IDS {g.d_review_ids.mean():+.2f} (p={C.wilcoxon_p(g.d_review_ids)[0]:.1e})")
L.append(f"(b) DFA alpha, speaker switches: {F.alpha_switch.mean():.3f} vs run-shuffled {F.alpha_switch_null.mean():.3f} (Wilcoxon p={C.wilcoxon_p(F.alpha_switch-F.alpha_switch_null)[0]:.1e}); %MaxEnt(15 s): {F.alpha_ent15.mean():.3f} vs {F.alpha_ent15_null.mean():.3f} (p={C.wilcoxon_p(F.alpha_ent15-F.alpha_ent15_null)[0]:.1e})")
L.append(f"(c) MSE complexity index (switch counts, scales 1-28 s): {M.CI.mean():.2f} vs run-shuffled {M.CI_null.mean():.2f} (Wilcoxon p={C.wilcoxon_p(M.CI-M.CI_null)[0]:.1e})")
L.append("    MSE curve obs/null by scale: " + " ".join(f"{s}:{M[f'se_{s}'].mean():.2f}/{M[f'null_{s}'].mean():.2f}" for s in range(1, 31, 3)))
for t in "AB":
    g = F[F.team == t]; m = M[M.team == t]
    L.append(f"  Team {t}: alpha_switch vs week tau={kendalltau(g.week, g.alpha_switch)[0]:+.2f} (p={kendalltau(g.week, g.alpha_switch)[1]:.2f}); MSE CI vs week tau={kendalltau(m.week, m.CI)[0]:+.2f} (p={kendalltau(m.week, m.CI)[1]:.2f})")
open(f"{C.RES}/multiscale_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
