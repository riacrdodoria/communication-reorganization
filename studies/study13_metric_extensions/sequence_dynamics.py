"""Sequence-only conversation dynamics (the transcripts give utterance onsets at 1-s resolution, speakers and text; no
offsets, so no latency, overlap or silence; back-channels are mostly dropped by the transcriber).
A. Participation shifts, sequence-only adaptation of Gibson (2003): for turn C after turns A, B (runs of one speaker):
   return (C = A, the AB-BA pattern), broaden (C new to the last two turns), re-entry (C silent >= 120 s before),
   facilitator entry, member-to-member transition. Window shares over the 120 s BEFORE each event, ending 30 s before
   onset ([-150, -30]), versus baseline windows >= 90 s from any event matched on mean %MaxEnt (nearest 3 per event,
   same meeting), so that the comparison is not driven by the entropy level that defines events. Also the turn that
   starts each event (first turn in [onset-5, onset+10]) versus entropy-matched turns.
B. What triggers reorganization. Conditional intensity of event onsets at lags after a trigger (events themselves,
   agenda-stage onsets, ends of extended floor turns, questions by facilitator / by members, re-entries), relative to
   the meeting's event rate, with 300 circular-shift 95 % bands. Hawkes model pooled over meetings with a meeting
   baseline and a gamma excitation kernel (delayed excitation allows the 30-60 s refractory dip), plus an exogenous
   gamma kernel from agenda onsets; compared with a Poisson model by AIC; branching ratio = share of events
   attributable to earlier events.
Output: results/seqdyn_*.csv, results/seqdyn_summary.txt"""
import sys, os, re, json, numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.stats import gamma as G, wilcoxon
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
rng = np.random.default_rng(131); P = json.load(open(f"{CM.RES}/partitions_bounds.json")); EV = CM.events()
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan
L = []; TURNS = []
for m in CM.meetings():
    tx = CM.transcript(m); tx = tx[tx.text.notna()].reset_index(drop=True); R = CM.roles(m)
    sp = tx.speaker_id.astype(str).to_numpy(); on = tx.onset_seconds.to_numpy(); txt = tx.text.astype(str).to_numpy()
    k = np.concatenate(([True], sp[1:] != sp[:-1])); st = np.flatnonzero(k); en = np.concatenate((st[1:], [len(sp)]))
    ts = on[st]; tsp = sp[st]; te = np.concatenate((ts[1:], [on.max() + 5])); q = np.array([any("?" in x for x in txt[a:b]) for a, b in zip(st, en)])
    ent = CM.metrics(m).set_index("second").entropy_g; last = {}
    for i in range(len(ts)):
        c = tsp[i]; role = R.get(c, "OTHER"); gap = ts[i] - last.get(c, -1e9); last[c] = te[i]
        a = tsp[i - 2] if i >= 2 else None; b = tsp[i - 1] if i >= 1 else None
        TURNS.append(dict(mid=m, t=ts[i], end=te[i], dur=te[i] - ts[i], spk=c, role=role, question=bool(q[i]),
                          ret=int(i >= 2 and c == a), broaden=int(i >= 2 and c != a and c != b), reentry=int(gap >= 120 and i > 0),
                          fac_in=int(role == "FACILITATOR"), m2m=int(i >= 1 and role != "FACILITATOR" and R.get(b, "OTHER") not in ("FACILITATOR", "OTHER") and role != "OTHER"),
                          ent=float(ent.iloc[np.argmin(np.abs(ent.index.to_numpy() - ts[i]))])))
T = pd.DataFrame(TURNS); T.to_csv(f"{CM.RES}/seqdyn_turns.csv", index=False)
FEATS = ["ret", "broaden", "reentry", "fac_in", "m2m", "question"]

# ---------- A1 precursor windows, entropy-matched baselines
rows = []
for m, g in T.groupby("mid"):
    ev = EV[EV.mid == m].event_onset_s.to_numpy(); ent = CM.metrics(m).set_index("second").entropy_g; Tm = P[m]["T"]
    def win(t0, t1):
        w = g[(g.t >= t0) & (g.t < t1)]; return w[FEATS].mean() if len(w) >= 3 else None
    cand = np.arange(200, Tm - 60, 10.0); cand = cand[np.min(np.abs(cand[:, None] - ev[None, :]), 1) >= 90] if ev.size else cand
    cent = np.array([ent.loc[(ent.index >= c - 150) & (ent.index < c - 30)].mean() for c in cand])
    for e in ev:
        if e < 180: continue
        we = win(e - 150, e - 30); ee = ent.loc[(ent.index >= e - 150) & (ent.index < e - 30)].mean()
        if we is None or np.isnan(ee): continue
        idx = np.argsort(np.abs(cent - ee))[:3]; wb = [win(c - 150, c - 30) for c in cand[idx]]; wb = [x for x in wb if x is not None]
        if not wb: continue
        rows.append(dict(mid=m, **{f"{f}_ev": we[f] for f in FEATS}, **{f"{f}_base": np.mean([x[f] for x in wb]) for f in FEATS}))
A1 = pd.DataFrame(rows); M1 = A1.groupby("mid").mean()
L.append("A1. PARTICIPATION SHIFTS IN THE 2 MIN BEFORE EVENTS ([-150, -30] s) vs ENTROPY-MATCHED BASELINES (meeting means; Wilcoxon)")
for f in FEATS:
    d = M1[f"{f}_ev"] - M1[f"{f}_base"]
    L.append(f"  {f:<9} pre-event {M1[f+'_ev'].mean():.3f} vs baseline {M1[f+'_base'].mean():.3f}  diff {d.mean():+.3f}  meetings + {int((d>0).sum())}/{len(d)}  p={wp(d):.3f}")

# ---------- A2 the turn that opens the event vs entropy-matched turns
rows = []
for m, g in T.groupby("mid"):
    ev = EV[EV.mid == m].event_onset_s.to_numpy(); g = g.reset_index(drop=True)
    far = g[np.min(np.abs(g.t.to_numpy()[:, None] - ev[None, :]), 1) >= 90] if ev.size else g
    for e in ev:
        o = g[(g.t >= e - 5) & (g.t <= e + 10)]
        if o.empty or far.empty: continue
        o = o.iloc[0]; mt = far.iloc[np.argsort(np.abs(far.ent.to_numpy() - o.ent))[:5]]
        rows.append(dict(mid=m, **{f"{f}_open": float(o[f]) for f in FEATS + ["dur"]}, **{f"{f}_match": mt[f].astype(float).mean() for f in FEATS + ["dur"]}))
A2 = pd.DataFrame(rows).groupby("mid").mean()
L.append("A2. THE TURN THAT OPENS AN EVENT vs 5 ENTROPY-MATCHED TURNS >= 90 s FROM EVENTS")
for f in FEATS + ["dur"]:
    d = A2[f"{f}_open"] - A2[f"{f}_match"]; L.append(f"  {f:<9} opening {A2[f+'_open'].mean():.3f} vs matched {A2[f+'_match'].mean():.3f}  p={wp(d):.3f}")

# ---------- B1 conditional intensity after triggers
LAGS = np.arange(-120, 300, 15)
def trig_sets(m):
    g = T[T.mid == m]; ev = EV[EV.mid == m].event_onset_s.to_numpy()
    return {"event": ev, "agenda": np.array(P[m]["agenda"]), "long-turn end": g[g.dur >= 30].end.to_numpy(),
            "question (facilitator)": g[g.question & (g.role == "FACILITATOR")].t.to_numpy(), "question (member)": g[g.question & (g.role != "FACILITATOR") & (g.role != "OTHER")].t.to_numpy(),
            "re-entry (>=120 s silent)": g[g.reentry == 1].t.to_numpy()}
def ci_curve(trig_of, shift=False):
    num = np.zeros(len(LAGS) - 1); den = np.zeros(len(LAGS) - 1)
    for m in CM.meetings():
        ev = EV[EV.mid == m].event_onset_s.to_numpy(); Tm = P[m]["T"]; tr = trig_of(m)
        if ev.size < 3 or tr.size == 0: continue
        if shift: tr = (tr + rng.uniform(0, Tm)) % Tm
        rate = ev.size / Tm
        for x in tr:
            d = ev - x; d = d[d != 0]
            num += np.histogram(d, LAGS)[0]; den += rate * np.diff(LAGS) * np.array([1 if 0 <= x + a and x + b <= Tm else 0 for a, b in zip(LAGS[:-1], LAGS[1:])])
    return num / np.maximum(den, 1e-9)
rows = []
L.append("B1. EVENT RATE AFTER EACH TRIGGER (observed / meeting rate; 95 % circular-shift band); lags in s")
for name in ["event", "agenda", "long-turn end", "question (facilitator)", "question (member)", "re-entry (>=120 s silent)"]:
    f = lambda m, n=name: trig_sets(m)[n]
    obs = ci_curve(f); nul = np.array([ci_curve(f, True) for _ in range(300)]); lo, hi = np.percentile(nul, [2.5, 97.5], 0)
    for a, o, l_, h_ in zip(LAGS[:-1], obs, lo, hi): rows.append(dict(trigger=name, lag=a, ratio=o, lo=l_, hi=h_))
    s = " ".join(f"{a:+d}:{o:.2f}{'+' if o > h_ else ('-' if o < l_ else '')}" for a, o, l_, h_ in zip(LAGS[:-1], obs, lo, hi))
    L.append(f"  {name:<26} {s}")
pd.DataFrame(rows).to_csv(f"{CM.RES}/seqdyn_intensity.csv", index=False)

# ---------- B2 Hawkes with gamma kernels
data = []
for m in CM.meetings():
    ev = np.sort(EV[EV.mid == m].event_onset_s.to_numpy()); data.append((ev, np.array(P[m]["agenda"]), P[m]["T"]))
def nll(theta, exo=True, self_=True):
    k = 0; mus = np.exp(theta[:len(data)]); k = len(data)
    a, ka, sa, g_, kg, sg = np.exp(theta[k:k + 6]) if len(theta) > k else (0, 1, 1, 0, 1, 1)
    if not self_: a = 0
    if not exo: g_ = 0
    ll = 0.0
    for (ev, ag, T_), mu in zip(data, mus):
        lam = np.full(ev.size, mu)
        if a > 0 and ev.size > 1:
            D = ev[:, None] - ev[None, :]; D = np.where(D > 0, D, np.nan); lam += a * np.nansum(G.pdf(D, ka, scale=sa), 1)
        if g_ > 0 and ag.size:
            D = ev[:, None] - ag[None, :]; D = np.where(D > 0, D, np.nan); lam += g_ * np.nansum(G.pdf(D, kg, scale=sg), 1)
        comp = mu * T_ + a * G.cdf(T_ - ev, ka, scale=sa).sum() + (g_ * G.cdf(T_ - ag, kg, scale=sg).sum() if ag.size else 0)
        ll += np.log(np.maximum(lam, 1e-12)).sum() - comp
    return -ll
mu0 = np.log([max(1, e.size) / T_ for e, _, T_ in data])
r0 = minimize(lambda th: nll(np.concatenate([th, np.log([1e-9, 1, 1, 1e-9, 1, 1])]), exo=False, self_=False), mu0, method="L-BFGS-B")
th0 = np.concatenate([mu0 + np.log(.6), np.log([.3, 3, 30, .3, 2, 30])])
r1 = minimize(nll, th0, method="L-BFGS-B", options={"maxiter": 3000})
r2 = minimize(lambda th: nll(th, exo=False), th0, method="L-BFGS-B", options={"maxiter": 3000})
k = len(data); a, ka, sa, g_, kg, sg = np.exp(r1.x[k:k + 6])
L.append("B2. HAWKES (gamma kernels, meeting baselines)")
L.append(f"  Poisson AIC {2*k + 2*r0.fun:.1f} | self-excitation only AIC {2*(k+6) + 2*r2.fun:.1f} | self + agenda AIC {2*(k+6) + 2*r1.fun:.1f}")
L.append(f"  branching ratio (share of events triggered by earlier events) {a:.3f}; self kernel mode {(ka-1)*sa if ka > 1 else 0:.0f} s, mean {ka*sa:.0f} s")
L.append(f"  agenda excitation: events per agenda onset {g_:.3f}; kernel mode {(kg-1)*sg if kg > 1 else 0:.0f} s, mean {kg*sg:.0f} s")
open(f"{CM.RES}/seqdyn_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
