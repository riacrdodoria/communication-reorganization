"""Midpoint transition test (Gersick, 1988) on the weekly trajectories of the longitudinal panel.
For each measure and team, y = a + b*meeting + c*after(k) + e, where after(k) = 1 for meetings k+1..17.
(1) Planned test: k = 10, the calendar midpoint (first and last meetings 14 Oct 2024 and 14 Apr 2025; meeting 10 on
    13 Jan 2025), which is also followed by the longest gap in the series. Pooled model with team intercepts and slopes and a
    common step; per-team models.
(2) Scan: F for the step over k = 4..13 (at least four meetings per segment); sup-F and best k.
(3) Global: mean F across all measures at each k, sup over k.
Nulls: residuals of the linear (no-step) model permuted within team, the same permutation applied to every measure in
the global test (keeps the correlation between measures), 2,000 permutations. BH-FDR across measures.
Reads results/longit_panel.csv; writes results/midpoint_break.csv and results/midpoint_break_summary.txt."""
import numpy as np, pandas as pd
import common as CM

R = CM.RES
MEASURES = {
    "turn-taking": ["entropy", "det", "switch", "active", "F1", "F2"],
    "floor & roles": ["fac_word_share", "centralization", "member_gini"],
    "events": ["event_rate", "event_depth", "events_anticipate_agenda"],
    "content": ["novelty", "topic_mixing", "sem_shift", "return_earlier", "new_lemmas_per_h"],
    "language": ["collective", "question", "sentiment"],
    "outcomes": ["rating_mean", "todo_completion_rate", "issue_resolution_rate_same_meeting", "n_issues_raised"],
}
KS = range(4, 14); K_PLANNED = 10; N_PERM = 2000


def design(w, team, k, step=True):
    cols = [np.ones_like(w, float), w.astype(float)]
    if team is not None:
        tb = (team == "B").astype(float); cols += [tb, tb * w]
    if step: cols.append((w > k).astype(float))
    return np.column_stack(cols)


def fit(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None); r = y - X @ beta; return beta, r @ r


def step_F(w, team, y, k):
    X0 = design(w, team, k, step=False); X1 = design(w, team, k)
    _, s0 = fit(X0, y); b1, s1 = fit(X1, y); df = len(y) - X1.shape[1]
    return (s0 - s1) / (s1 / df), b1[-1]


def null_y(w, team, y, rng):
    X0 = design(w, team, 0, step=False); b, _ = fit(X0, y); yhat = X0 @ b; r = y - yhat
    rp = r.copy()
    groups = [np.ones(len(y), bool)] if team is None else [team == t for t in ("A", "B")]
    for g in groups: idx = np.where(g)[0]; rp[idx] = r[rng.permutation(idx)]
    return yhat + rp


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); q = np.empty(n); prev = 1.0
    for i, j in enumerate(o[::-1]):
        rank = n - i; prev = min(prev, p[j] * n / rank); q[j] = prev
    return q


if __name__ == "__main__":
    D = pd.read_csv(f"{R}/longit_panel.csv").sort_values(["team", "week"]).reset_index(drop=True)
    rng = np.random.default_rng(7)
    allm = [(fam, v) for fam, vs in MEASURES.items() for v in vs if v in D]
    sets = {"pooled": (D, True), "A": (D[D.team == "A"], False), "B": (D[D.team == "B"], False)}
    rows = []; glob = {}
    for sname, (S, pooled) in sets.items():
        w = S.week.to_numpy(); team = S.team.to_numpy() if pooled else None
        Ys = {v: S[v].to_numpy(float) for _, v in allm}
        ok = {v: ~np.isnan(y) for v, y in Ys.items()}
        obs = {v: {k: step_F(w[ok[v]], None if team is None else team[ok[v]], Ys[v][ok[v]], k) for k in KS} for v in Ys}
        # null: one permutation index per draw, shared across measures (complete-case measures only share it exactly)
        nullF = {v: np.zeros((N_PERM, len(KS))) for v in Ys}
        for i in range(N_PERM):
            seed = rng.integers(1 << 31)
            for v, y in Ys.items():
                r_ = np.random.default_rng(seed); m = ok[v]; ww = w[m]; tt = None if team is None else team[m]
                yn = null_y(ww, tt, y[m], r_)
                nullF[v][i] = [step_F(ww, tt, yn, k)[0] for k in KS]
        for fam, v in allm:
            F = np.array([obs[v][k][0] for k in KS]); kbest = list(KS)[int(np.argmax(F))]
            iP = list(KS).index(K_PLANNED)
            p_planned = (np.sum(nullF[v][:, iP] >= F[iP]) + 1) / (N_PERM + 1)
            p_sup = (np.sum(nullF[v].max(1) >= F.max()) + 1) / (N_PERM + 1)
            rows.append(dict(set=sname, family=fam, measure=v, step_at_10=obs[v][K_PLANNED][1], F_at_10=F[iP], p_at_10=p_planned,
                             best_k=kbest, step_at_best=obs[v][kbest][1], supF=F.max(), p_sup=p_sup,
                             sd=np.nanstd(Ys[v])))
        G = np.mean([[obs[v][k][0] for k in KS] for v in Ys], 0); Gn = np.mean([nullF[v] for v in Ys], 0)
        glob[sname] = dict(meanF=G, p_planned=(np.sum(Gn[:, list(KS).index(K_PLANNED)] >= G[list(KS).index(K_PLANNED)]) + 1) / (N_PERM + 1),
                           kbest=list(KS)[int(np.argmax(G))], p_sup=(np.sum(Gn.max(1) >= G.max()) + 1) / (N_PERM + 1))
    T = pd.DataFrame(rows)
    for s in sets:
        m = T.set == s; T.loc[m, "q_at_10"] = bh(T.loc[m, "p_at_10"]); T.loc[m, "q_sup"] = bh(T.loc[m, "p_sup"])
    T["step_at_10_sd"] = T.step_at_10 / T.sd
    T.to_csv(f"{R}/midpoint_break.csv", index=False)
    L = ["MIDPOINT TRANSITION TEST (step beyond a linear trend; residual permutation, %d draws)" % N_PERM,
         "Planned break after meeting 10 (calendar midpoint, 13 Jan 2025; followed by the longest gap in the series).", ""]
    for s in sets:
        g = glob[s]
        L.append(f"[{s}] GLOBAL mean F across {len(allm)} measures: at k=10 {g['meanF'][list(KS).index(K_PLANNED)]:.2f} (p={g['p_planned']:.3f}); "
                 f"best k={g['kbest']} (sup p={g['p_sup']:.3f}); mean F by k: " + " ".join(f"{k}:{f:.2f}" for k, f in zip(KS, g["meanF"])))
        S = T[T.set == s].sort_values("p_at_10")
        for r in S.itertuples():
            L.append(f"   {r.family:<13} {r.measure:<36} step@10 {r.step_at_10_sd:+.2f} SD  p={r.p_at_10:.3f} q={r.q_at_10:.2f} | best k={r.best_k:<2} supF p={r.p_sup:.3f} q={r.q_sup:.2f}")
        L.append("")
    open(f"{R}/midpoint_break_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
