"""Item 1. Gorman & Wiltshire (2024) typology: System I (fixed point), II (periodic, stable), III (periodic, changing).
Operationalization (exploratory). The %MaxEnt series (60-s window, 1-s step) of each meeting is split into thirds.
In each third, a Welch periodogram is compared with the periodograms of 200 run-shuffled surrogates: the team-state
runs (maximal stretches of one state on the 2 Hz grid) are permuted, which keeps the run-length distribution and the
windowing but destroys temporal organization, and the entropy series is recomputed with the same window (this is the
null of Study 1). Statistic: max over periods 2-20 min of observed / mean-surrogate power; p = (b+1)/(N+1).
System I = no third periodic; II = >= 2 thirds periodic with dominant periods within a factor 1.5; III = otherwise.
Output: results/typology_meetings.csv, results/typology_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.signal import welch
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(13); HZ = 2; WIN = 121; STEP = 2; NSUR = 200
PMIN, PMAX = 120, 1200

def entropy_series(state, nsp):
    vals = np.unique(state); maxbits = nsp
    cs = {v: np.concatenate(([0], np.cumsum(state == v))) for v in vals}
    centers = np.arange(WIN // 2, state.size - WIN // 2, STEP); a = centers - WIN // 2; b = a + WIN
    H = np.zeros(centers.size)
    for v in vals:
        p = (cs[v][b] - cs[v][a]) / WIN; nz = p > 0; H[nz] -= p[nz] * np.log2(p[nz])
    return 100 * H / maxbits

def runs(state):
    cut = np.flatnonzero(np.diff(state)) + 1; return np.split(state, cut)

def shuffled(state):
    r = runs(state); return np.concatenate([r[i] for i in rng.permutation(len(r))])

def psd(x, nps):
    x = x - np.polyval(np.polyfit(np.arange(x.size), x, 1), np.arange(x.size)); return welch(x, fs=1.0, nperseg=nps)

if __name__ == "__main__":
    W = C.week_map(); E = C.events(); rows = []
    for mid in C.meetings():
        state, nsp = C.team_state(mid); x = entropy_series(state, nsp)
        sur = [entropy_series(shuffled(state), nsp) for _ in range(NSUR)]
        res = []
        for k, idx in enumerate(np.array_split(np.arange(x.size), 3)):
            nps = min(idx.size, 1024); f, P = psd(x[idx], nps); band = (f >= 1 / PMAX) & (f <= 1 / PMIN)
            PS = np.array([psd(s[idx[idx < s.size]], nps)[1] for s in sur]); ref = PS.mean(0)
            stat = (P[band] / ref[band]).max(); null = (PS[:, band] / ref[band]).max(1)
            res.append(((np.sum(null >= stat) + 1) / (NSUR + 1), 1 / f[band][np.argmax(P[band] / ref[band])]))
        sig = [p < .05 for p, _ in res]; per = [q for (p, q), s in zip(res, sig) if s]
        if sum(sig) == 0: sysl = "I"
        elif sum(sig) >= 2 and max(per) / min(per) <= 1.5: sysl = "II"
        else: sysl = "III"
        ne = (E.mid == mid).sum(); dur = x.size / 60
        rows.append(dict(mid=mid, team=C.team(mid), week=W[mid], system=sysl, n_periodic_thirds=sum(sig), p_thirds=";".join(f"{p:.3f}" for p, _ in res),
                         periods_min=";".join(f"{q/60:.1f}" for q in per), events_per_10min=10 * ne / dur, mean_entropy=x.mean(), sd_entropy=x.std(),
                         sd_ratio_to_shuffle=x.std() / np.mean([s.std() for s in sur])))
        print(mid, sysl, [f"{p:.3f}" for p, _ in res], [f"{q/60:.1f}" for q in per], flush=True)
    T = pd.DataFrame(rows); T.to_csv(f"{C.RES}/typology_meetings.csv", index=False)
    L = ["Counts by system and team:", pd.crosstab(T.system, T.team).to_string(), "",
         f"Entropy SD relative to run-shuffled surrogates: mean ratio {T.sd_ratio_to_shuffle.mean():.2f} (range {T.sd_ratio_to_shuffle.min():.2f}-{T.sd_ratio_to_shuffle.max():.2f})"]
    for s in ["I", "II", "III"]:
        g = T[T.system == s]
        if len(g): L.append(f"System {s}: n={len(g)} events/10min {g.events_per_10min.mean():.2f} mean entropy {g.mean_entropy.mean():.1f} sd {g.sd_entropy.mean():.1f}")
    num = T.system.map({"I": 1, "II": 2, "III": 3})
    for t, g in T.groupby("team"):
        tau, p = kendalltau(g.week, num[g.index]); L.append(f"Team {t}: system rank vs week tau={tau:+.2f} p={p:.2f}")
    tau, p = kendalltau(num, T.events_per_10min); L.append(f"system rank vs event rate tau={tau:+.2f} p={p:.3f}")
    open(f"{C.RES}/typology_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
