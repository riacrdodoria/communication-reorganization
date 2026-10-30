"""Item 5. Relational-event model of turn allocation (Butts, 2008; conditional logit over the risk set).
Turns = runs of consecutive utterances by the same speaker. For each turn t >= 2, the risk set is every meeting
participant except the current speaker; the outcome is who takes the next turn.
Candidate-level predictors: recip (candidate held turn t-1, i.e. AB->BA return), recency (log seconds since the
candidate last spoke, capped at 600), share (candidate's share of turns so far), fac (candidate holds the facilitator role).
Turn-level moderators (enter only as interactions, since conditional logit absorbs turn constants):
near = next-turn onset within +/-30 s of an RMSE event onset; week_z = meeting week, z-scored within team;
ids = turn inside the IDS stage.
Models: M1 base; M2 + near interactions; M3 + week interactions; M4 + ids interactions; fitted pooled with turn groups.
Output: results/rem_coefs.csv, results/rem_summary.txt"""
import sys, os, numpy as np, pandas as pd
from statsmodels.discrete.conditional_models import ConditionalLogit
sys.path.insert(0, os.path.dirname(__file__)); import common as C

if __name__ == "__main__":
    E = C.events(); Wk = C.week_map(); rows = []; gid = 0
    wk = pd.Series(Wk); wz = {m: (Wk[m] - wk[[x for x in wk.index if C.team(x) == C.team(m)]].mean()) / wk[[x for x in wk.index if C.team(x) == C.team(m)]].std() for m in Wk}
    for mid in C.meetings():
        tx = C.transcript(mid); R = C.roles(mid); sp = tx.speaker_id.astype(str).to_numpy(); on = tx.onset_seconds.to_numpy()
        keep = np.concatenate(([True], sp[1:] != sp[:-1])); sp, on = sp[keep], on[keep]
        people = sorted(set(sp)); ev = E[E.mid == mid].event_onset_s.to_numpy()
        stl = C.stage_of_seconds(mid, on)
        last = {p: -np.inf for p in people}; cnt = {p: 0 for p in people}
        for t in range(len(sp) - 1):
            last[sp[t]] = on[t]; cnt[sp[t]] += 1
            if t < 1: continue
            nxt = sp[t + 1]; near = float(ev.size > 0 and np.min(np.abs(ev - on[t + 1])) <= 30); ids = float(stl[t + 1] == "ids"); tot = sum(cnt.values())
            for p in people:
                if p == sp[t]: continue
                rec = min(600.0, on[t + 1] - last[p]) if np.isfinite(last[p]) else 600.0
                rows.append(dict(g=gid, mid=mid, y=int(p == nxt), recip=float(p == sp[t - 1]), recency=np.log1p(rec), share=cnt[p] / tot,
                                 fac=float(R.get(p, "OTHER") == "FACILITATOR"), near=near, week_z=wz[mid], ids=ids))
            gid += 1
        print(mid, gid, flush=True)
    D = pd.DataFrame(rows); D = D[D.groupby("g").y.transform("sum") == 1]
    base = ["recip", "recency", "share", "fac"]
    for b in base:
        for m in ["near", "week_z", "ids"]: D[f"{b}_x_{m}"] = D[b] * D[m]
    specs = {"M1": base, "M2": base + [f"{b}_x_near" for b in base], "M3": base + [f"{b}_x_week_z" for b in base], "M4": base + [f"{b}_x_ids" for b in base],
             "M5": base + [f"{b}_x_{m}" for b in base for m in ["near", "week_z", "ids"]]}
    out = []; L = [f"Turns (choice sets): {D.g.nunique()}; candidate rows: {len(D)}; meetings: {D.mid.nunique()}"]
    for name, X in specs.items():
        r = ConditionalLogit(D.y, D[X], groups=D.g).fit(disp=False, maxiter=3000, gtol=1e-6)
        for v in X: out.append(dict(model=name, term=v, coef=r.params[v], se=r.bse[v], z=r.tvalues[v], p=r.pvalues[v], OR=np.exp(r.params[v])))
        L.append(f"\n{name}  logLik={r.llf:.1f}  AIC={2*len(X)-2*r.llf:.1f}")
        for v in X: L.append(f"  {v:<18} b={r.params[v]:+.3f} (OR {np.exp(r.params[v]):.2f})  z={r.tvalues[v]:+.2f}  p={r.pvalues[v]:.1e}")
    # team-specific week drift of reciprocity (routinization check)
    for t in "AB":
        d = D[D.mid.map(C.team) == t]; X = base + ["recip_x_week_z", "fac_x_week_z"]; r = ConditionalLogit(d.y, d[X], groups=d.g).fit(disp=False, maxiter=3000, gtol=1e-6)
        L.append(f"\nTeam {t}: recip x week b={r.params['recip_x_week_z']:+.3f} p={r.pvalues['recip_x_week_z']:.1e}; fac x week b={r.params['fac_x_week_z']:+.3f} p={r.pvalues['fac_x_week_z']:.1e}")
    pd.DataFrame(out).to_csv(f"{C.RES}/rem_coefs.csv", index=False); open(f"{C.RES}/rem_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
