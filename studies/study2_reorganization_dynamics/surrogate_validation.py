"""
surrogate_validation.py — Is the Study 2 'aggregation/regimes' finding a real
contribution or a trivial consequence of peak-triggered differencing on an
oscillating signal? Tests OBSERVED vs two nulls that also oscillate:

  - AR(1) per series (independent): preserves each series' autocorrelation.
  - VAR(1) bivariate: ALSO preserves the contemporaneous + lagged entropy-determinism
    coupling. The strict null for the coupling question.

Statistics compared at deterministic UCL peaks (mean+2SD local maxima, +/-90s windows):
  - pooled Delta-entropy p  (cancellation; expected ~n.s. under any oscillating null)
  - SD(Delta-entropy)       (reorganization magnitude)
  - corr(Delta-ent, Delta-det) (order<->disorder coupling)

Run: ./.venv/bin/python surrogate_validation.py [N_surrogates=200] [--legacy]

SOURCE (2026-09-05): default = the Gorman-faithful L_min=8 metrics (data/metrics_gorman_l8, %MaxEnt units).
`--legacy` reproduces the earlier run on data/processed/metrics_startup (1 Hz LSH, raw bits, %DET L_min=2),
which is what the published 0.405 vs 0.190 numbers came from.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp, pearsonr

ROOT = Path(__file__).resolve().parent
LEGACY = "--legacy" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
M = ROOT / ("data/processed/metrics_startup" if LEGACY else "data/metrics_gorman_l8")
SUF, ECOL, DCOL = ("_entropy.csv", "entropy_lsh", "det_lsh") if LEGACY else ("_gorman.csv", "entropy_g", "det_g")
NS = int(ARGS[0]) if ARGS else 200
K, W, SEP = 2.0, 90, 60

def load():
    o = {}
    for mp in sorted(M.glob(f"*{SUF}")):
        d = pd.read_csv(mp).sort_values("second").drop_duplicates("second").reset_index(drop=True)
        d = d.rename(columns={ECOL: "entropy", DCOL: "det"}).dropna(subset=["entropy", "det"]).reset_index(drop=True)
        o[mp.name.replace(SUF, "")] = d
    return o

def feats(ent, det, k=K, w=W, sep=SEP):
    n = len(ent); thr = ent.mean() + k * ent.std(ddof=1); cand = []
    for i in range(1, n - 1):
        if ent[i] > thr and ent[i] >= ent[i-1] and ent[i] >= ent[i+1]:
            cand.append((i, ent[i]))
    cand.sort(key=lambda x: -x[1]); kept = []; u = []
    for i, v in cand:
        if all(abs(i - x) >= sep for x in u): kept.append(i); u.append(i)
    r = []
    for i in kept:
        if i - w < 0 or i + w >= n: continue
        r.append((ent[i+1:i+w+1].mean() - ent[i-w:i].mean(),
                  det[i+1:i+w+1].mean() - det[i-w:i].mean()))
    return r

def fit_ar1(x):
    x = np.asarray(x, float); y = x[1:]; X = np.column_stack([np.ones(len(x)-1), x[:-1]])
    b = np.linalg.lstsq(X, y, rcond=None)[0]; res = y - (b[0] + b[1]*x[:-1])
    return b[1], b[0], np.std(res, ddof=1)

def sim_ar1(n, phi, c, sig, rng, x0):
    o = np.empty(n); o[0] = x0
    for i in range(1, n): o[i] = c + phi*o[i-1] + rng.normal(0, sig)
    return o

def fit_var1(E, D):
    Z = np.column_stack([E, D]); X = np.column_stack([np.ones(len(Z)-1), Z[:-1]]); Y = Z[1:]
    B = np.linalg.lstsq(X, Y, rcond=None)[0]; resid = Y - X @ B
    return B[0], B[1:].T, np.cov(resid.T)

def sim_var1(n, c, A, Sig, rng, z0):
    L = np.linalg.cholesky(Sig + 1e-12*np.eye(2)); Z = np.empty((n, 2)); Z[0] = z0
    for t in range(1, n): Z[t] = c + A @ Z[t-1] + L @ rng.standard_normal(2)
    return Z[:, 0], Z[:, 1]

def summarize(rows):
    fr = pd.DataFrame(rows, columns=["de", "dd"])
    return (ttest_1samp(fr.de, 0).pvalue, fr.de.std(ddof=1), pearsonr(fr.de, fr.dd)[0], len(fr))

def main():
    meet = load()
    obs = []
    for mid, df in meet.items():
        obs += feats(df["entropy"].to_numpy(float), df["det"].to_numpy(float))
    o_p, o_sd, o_r, o_n = summarize(obs)
    print(f"SOURCE: {M}  ({'raw bits, L_min=2' if LEGACY else '%MaxEnt, L_min=8'})")
    print(f"OBSERVED: N={o_n}  pooled p={o_p:.3f}  SD(Δent)={o_sd:.3f}  corr(Δent,Δdet)={o_r:.3f}\n")

    results = dict(source="legacy_bits_Lmin2" if LEGACY else "gorman_L8_pctMaxEnt", n_events=o_n, obs_sd=o_sd, obs_r=o_r)
    rng = np.random.default_rng(42)
    for name in ("AR1", "VAR1"):
        ps, sds, rs = [], [], []
        if name == "AR1":
            par = {m: (fit_ar1(d["entropy"]), fit_ar1(d["det"]), len(d),
                       d["entropy"].mean(), d["det"].mean()) for m, d in meet.items()}
        else:
            par = {m: (fit_var1(d["entropy"].to_numpy(float), d["det"].to_numpy(float)),
                       len(d), d["entropy"].mean(), d["det"].mean()) for m, d in meet.items()}
        for s in range(NS):
            rows = []
            for m, P in par.items():
                if name == "AR1":
                    ae, ad, n, e0, d0 = P
                    e = sim_ar1(n, *ae, rng, e0); d = sim_ar1(n, *ad, rng, d0)
                else:
                    (c, A, Sig), n, e0, d0 = P
                    e, d = sim_var1(n, c, A, Sig, rng, np.array([e0, d0]))
                rows += feats(e, d)
            if len(rows) < 12: continue
            p, sd, r, _ = summarize(rows); ps.append(p); sds.append(sd); rs.append(r)
        ps, sds, rs = map(np.array, (ps, sds, rs))
        def verdict(o, null, lower=True):
            lo, hi = np.percentile(null, [2.5, 97.5])
            ex = (o < lo) if lower else (o > hi)
            return f"[{lo:.3f},{hi:.3f}] -> {'EXCEEDS' if ex else 'within'}"
        print(f"{name} NULL ({NS} runs):")
        print(f"  pooled cancels in {(ps>0.05).mean()*100:.0f}% of runs (mean p={ps.mean():.3f})  [cancellation is null-expected]")
        print(f"  SD(Δent):  null mean={sds.mean():.3f} {verdict(o_sd, sds, lower=False)}")
        print(f"  corr:      null mean={rs.mean():.3f} {verdict(o_r, rs, lower=True)}\n")
        lo, hi = np.percentile(sds, [2.5, 97.5]); results.update({f"{name}_sd_mean": sds.mean(), f"{name}_sd_lo": lo, f"{name}_sd_hi": hi})
        lo, hi = np.percentile(rs, [2.5, 97.5]); results.update({f"{name}_r_mean": rs.mean(), f"{name}_r_lo": lo, f"{name}_r_hi": hi})
    out = ROOT / ("surrogate_validation_results_legacy.csv" if LEGACY else "surrogate_validation_results.csv")
    pd.DataFrame([results]).to_csv(out, index=False); print(f"wrote {out.name}")

if __name__ == "__main__":
    main()
