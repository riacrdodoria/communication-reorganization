"""Item 3. Metric-comparison battery on the same team-state series and windows (60 s, step 5 s, 2 Hz grid).
Metrics: %MaxEnt, %DET (L_min 8), recurrence rate RR, laminarity LAM and trapping time TT (vertical lines >= 2 samples,
line of identity excluded), Lempel-Ziv complexity (LZ76, normalized), conditional entropy H(X_t | X_t-1) on the 2 Hz
grid, switch rate (state changes per minute), active speakers, top-speaker share, silence share.
Analyses: (i) mean within-meeting Spearman correlation matrix; (ii) PCA on within-meeting z-scores (pooled);
(iii) event sensitivity: per meeting, metric in windows centred within +/-15 s of an event onset vs baseline windows
(>= 90 s from any event), standardized difference d, Wilcoxon across meetings; (iv) the same at topic-episode
boundaries (+/-15 s) vs interiors (>= 60 s from a boundary).
Output: results/battery_windows.csv, battery_corr.csv, battery_pca.csv, battery_sensitivity.csv, battery_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(__file__)); import common as C
sys.path.insert(0, C.L + "/study1_lsh_validation")
WIN = 121; STEP = 10; VMIN = 2

def det_lam(seg, lmin=8, vmin=VMIN):
    n = seg.size; rec = 0; diag = 0
    for off in range(1, n):
        d = seg[:n - off] == seg[off:]
        if not d.any(): continue
        rec += int(d.sum()); pad = np.concatenate(([False], d, [False])); e = np.flatnonzero(pad[1:] != pad[:-1]); r = e[1::2] - e[0::2]; diag += int(r[r >= lmin].sum())
    # vertical structure, line of identity excluded (exact for categorical series)
    cut = np.flatnonzero(np.diff(seg)) + 1; starts = np.concatenate(([0], cut)); lens = np.diff(np.concatenate((starts, [n]))); vals = seg[starts]
    lam_pts = 0; tot_pts = 0; n_lines = 0
    for v in np.unique(vals):
        rl = lens[vals == v]; n_v = rl.sum()
        for r in rl:  # columns inside a run of length r: the run splits into pieces above and below the diagonal
            others = rl[rl >= vmin]; o_sum = others.sum() - (r if r >= vmin else 0); o_cnt = len(others) - (1 if r >= vmin else 0)
            p = np.arange(r); a = p; b = r - 1 - p
            lam_pts += r * o_sum + a[a >= vmin].sum() + b[b >= vmin].sum()
            n_lines += r * o_cnt + int((a >= vmin).sum()) + int((b >= vmin).sum())
            tot_pts += r * (n_v - 1)
    rr = 2 * rec / (n * (n - 1)); det = 100 * diag / rec if rec else 0.0
    lam = 100 * lam_pts / tot_pts if tot_pts else 0.0; tt = lam_pts / n_lines / 2 if n_lines else 0.0  # TT in seconds (2 Hz)
    return rr, det, lam, tt

def lz76(s):
    """Lempel-Ziv (1976) complexity, Kaspar-Schuster algorithm, normalized by n / log_a(n)."""
    s = list(s); n = len(s); i, k, l, c, kmax = 0, 1, 1, 1, 1
    while True:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
            if l + k > n: c += 1; break
        else:
            kmax = max(k, kmax); i += 1
            if i == l:
                c += 1; l += kmax
                if l + 1 > n: break
                i, k, kmax = 0, 1, 1
            else:
                k = 1
    a = max(2, len(set(s))); return c * np.log(n) / np.log(a) / n

def window_metrics(seg, nsp):
    vals, cnt = np.unique(seg, return_counts=True); p = cnt / cnt.sum(); ent = 100 * -(p * np.log2(p)).sum() / nsp
    pairs = seg[:-1] * 100000 + seg[1:]; pv, pc = np.unique(pairs, return_counts=True); pj = pc / pc.sum()
    prev, pcnt = np.unique(seg[:-1], return_counts=True); pp = pcnt / pcnt.sum()
    condH = -(pj * np.log2(pj)).sum() + (pp * np.log2(pp)).sum()
    rr, det, lam, tt = det_lam(seg)
    single = [(v, c) for v, c in zip(vals, cnt) if v != 0 and (v & (v - 1)) == 0]
    top = max([c for _, c in single], default=0) / max(1, sum(c for v, c in zip(vals, cnt) if v != 0))
    active = len({i for v in vals for i in range(nsp) if (v >> i) & 1})
    return dict(entropy=ent, det=det, RR=rr, LAM=lam, TT=tt, LZ=lz76(seg), condH=condH, switch=60 * np.sum(seg[1:] != seg[:-1]) / (seg.size / 2),
                active=active, top_share=top, silence=(seg == 0).mean())

E = C.events(); rows = []
for mid in C.meetings():
    st, nsp = C.team_state(mid); ev = E[E.mid == mid].event_onset_s.to_numpy(); bd = C.episode_bounds(mid)
    for c in range(WIN // 2, st.size - WIN // 2, STEP):
        sec = c / 2; m = window_metrics(st[c - WIN // 2:c + WIN // 2 + 1], nsp)
        de = np.min(np.abs(ev - sec)) if ev.size else 1e9; db = np.min(np.abs(bd - sec)) if bd.size else 1e9
        rows.append(dict(mid=mid, sec=sec, near_event=de <= 15, base_event=de >= 90, near_bound=db <= 15, interior=db >= 60, **m))
    print(mid, flush=True)
D = pd.DataFrame(rows); D.to_csv(f"{C.RES}/battery_windows.csv", index=False)
M = ["entropy", "det", "RR", "LAM", "TT", "LZ", "condH", "switch", "active", "top_share", "silence"]
cors = [D[D.mid == m][M].corr(method="spearman").to_numpy() for m in D.mid.unique()]
CM = pd.DataFrame(np.nanmean(cors, 0), index=M, columns=M).round(2); CM.to_csv(f"{C.RES}/battery_corr.csv")
Z = D.groupby("mid")[M].transform(lambda x: (x - x.mean()) / (x.std() if x.std() > 0 else 1)).dropna()
U, S, Vt = np.linalg.svd(Z.to_numpy() - Z.to_numpy().mean(0), full_matrices=False); ve = S ** 2 / (S ** 2).sum()
PCA = pd.DataFrame(Vt[:3].T, index=M, columns=["PC1", "PC2", "PC3"]).round(2); PCA.to_csv(f"{C.RES}/battery_pca.csv")
sens = []
for metric in M:
    for name, a, b in [("event", "near_event", "base_event"), ("boundary", "near_bound", "interior")]:
        d = []
        for mid, g in D.groupby("mid"):
            x, y = g[g[a]][metric], g[g[b]][metric]; sd = g[metric].std()
            if len(x) > 2 and len(y) > 2 and sd > 0: d.append((x.mean() - y.mean()) / sd)
        p, n = C.wilcoxon_p(d); sens.append(dict(metric=metric, anchor=name, mean_d=np.mean(d), n_pos=int(np.sum(np.array(d) > 0)), n=n, p=p))
SE = pd.DataFrame(sens); SE.to_csv(f"{C.RES}/battery_sensitivity.csv", index=False)
L = ["Mean within-meeting Spearman correlations:", CM.to_string(), "", f"PCA variance explained: {ve[:3].round(3)}", PCA.to_string(), "", "Sensitivity (standardized difference, Wilcoxon across meetings):",
     SE.pivot(index="metric", columns="anchor", values="mean_d").round(2).to_string(), "", SE.round(4).to_string(index=False)]
open(f"{C.RES}/battery_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
