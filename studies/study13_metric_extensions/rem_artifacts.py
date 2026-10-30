"""Artifact checks for 'the floor opens at reorganization' (rem.py: reciprocity and facilitator advantage weaker within
+/-30 s of events). Events are detected where turn-taking structure changes, so the effect could simply reflect high
local entropy (more speakers active), not the event.
(1) Control: add interactions of every base term with local %MaxEnt (z within meeting, metric second nearest to the
    next-turn onset) and with the local count of distinct speakers in the previous 60 s.
(2) Placebo: 'near_peak' = within +/-30 s of an entropy peak that is NOT an event (local maxima above the meeting's 90th
    percentile, >= 90 s from every event, >= 60 s apart). If the placebo gives the same interactions, the effect is about
    high entropy, not events.
(3) Circular-shift null: event times shifted by a random offset within each meeting (100 draws), model (1) refitted;
    the observed near interactions are compared with this distribution.
Output: results/rem_artifacts.csv, results/rem_artifacts_summary.txt"""
import sys, os, numpy as np, pandas as pd
from statsmodels.discrete.conditional_models import ConditionalLogit
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(71); NSH = 100

E = C.events(); rows = []; gid = 0; META = {}
for mid in C.meetings():
    tx = C.transcript(mid); R = C.roles(mid); sp = tx.speaker_id.astype(str).to_numpy(); on = tx.onset_seconds.to_numpy()
    keep = np.concatenate(([True], sp[1:] != sp[:-1])); sp, on = sp[keep], on[keep]
    people = sorted(set(sp)); ev = E[E.mid == mid].event_onset_s.to_numpy()
    g = C.metrics(mid).set_index("second").entropy_g; z = (g - g.mean()) / g.std(); secs = g.index.to_numpy()
    # placebo peaks
    e = g.to_numpy(); thr = np.percentile(e, 90); cand = [i for i in range(1, e.size - 1) if e[i] >= thr and e[i] >= e[i - 1] and e[i] >= e[i + 1]]
    cand = sorted(cand, key=lambda i: -e[i]); pk = []
    for i in cand:
        s = secs[i]
        if (ev.size == 0 or np.min(np.abs(ev - s)) >= 90) and all(abs(s - x) >= 60 for x in pk): pk.append(s)
    pk = np.array(pk); T = on.max(); META[mid] = (ev, T)
    last = {p: -np.inf for p in people}; cnt = {p: 0 for p in people}
    for t in range(len(sp) - 1):
        last[sp[t]] = on[t]; cnt[sp[t]] += 1
        if t < 1: continue
        tn = on[t + 1]; nxt = sp[t + 1]; tot = sum(cnt.values())
        ez = float(z.iloc[np.argmin(np.abs(secs - tn))]); nspk = len(set(sp[(on >= tn - 60) & (on < tn)]))
        near = float(ev.size > 0 and np.min(np.abs(ev - tn)) <= 30); nearpk = float(pk.size > 0 and np.min(np.abs(pk - tn)) <= 30)
        for p in people:
            if p == sp[t]: continue
            rec = min(600.0, tn - last[p]) if np.isfinite(last[p]) else 600.0
            rows.append(dict(g=gid, mid=mid, t_on=tn, y=int(p == nxt), recip=float(p == sp[t - 1]), recency=np.log1p(rec), share=cnt[p] / tot,
                             fac=float(R.get(p, "OTHER") == "FACILITATOR"), near=near, near_peak=nearpk, ent_z=ez, nspk=nspk))
        gid += 1
    print(mid, len(pk), "placebo peaks", flush=True)
D = pd.DataFrame(rows); D = D[D.groupby("g").y.transform("sum") == 1].reset_index(drop=True)
D["nspk_z"] = (D.nspk - D.nspk.mean()) / D.nspk.std()
base = ["recip", "recency", "share", "fac"]
def add(D, mod):
    for b in base: D[f"{b}_x_{mod}"] = D[b] * D[mod]
for m in ["near", "near_peak", "ent_z", "nspk_z"]: add(D, m)
ctrl = [f"{b}_x_{m}" for b in base for m in ["ent_z", "nspk_z"]]
specs = {"near only": base + [f"{b}_x_near" for b in base],
         "near + local-entropy controls": base + [f"{b}_x_near" for b in base] + ctrl,
         "placebo peaks only": base + [f"{b}_x_near_peak" for b in base],
         "placebo + controls": base + [f"{b}_x_near_peak" for b in base] + ctrl,
         "near + placebo + controls": base + [f"{b}_x_near" for b in base] + [f"{b}_x_near_peak" for b in base] + ctrl}
out = []; L = [f"Choice sets {D.g.nunique()}; turns near events {D.groupby('g').near.first().mean():.3f}; near placebo peaks {D.groupby('g').near_peak.first().mean():.3f}"]
for name, X in specs.items():
    r = ConditionalLogit(D.y, D[X], groups=D.g).fit(disp=False, maxiter=3000, gtol=1e-6)
    L.append(f"\n{name}  logLik={r.llf:.1f}")
    for v in X:
        if "near" in v or v in ("recip", "fac") or "ent_z" in v:
            L.append(f"  {v:<20} OR={np.exp(r.params[v]):.3f}  p={r.pvalues[v]:.1e}")
        out.append(dict(model=name, term=v, coef=r.params[v], se=r.bse[v], p=r.pvalues[v]))
# circular-shift null for the controlled model
X = specs["near + local-entropy controls"]; obs = {v: [o["coef"] for o in out if o["model"] == "near + local-entropy controls" and o["term"] == v][0] for v in ["recip_x_near", "fac_x_near"]}
null = {v: [] for v in obs}
for k in range(NSH):
    nn = np.zeros(len(D))
    for mid, (ev, T) in META.items():
        idx = np.flatnonzero(D.mid.to_numpy() == mid)
        if ev.size == 0: continue
        sh = (ev + rng.uniform(0, T)) % T; tn = D.t_on.to_numpy()[idx]
        nn[idx] = (np.min(np.abs(tn[:, None] - sh[None, :]), 1) <= 30).astype(float)
    Dk = D.copy(); Dk["near"] = nn; add(Dk, "near")
    r = ConditionalLogit(Dk.y, Dk[X], groups=Dk.g).fit(disp=False, maxiter=3000, gtol=1e-6)
    for v in null: null[v].append(r.params[v])
    if k % 20 == 0: print("shift", k, {v: round(null[v][-1], 3) for v in null}, flush=True)
L.append("\nCircular-shift null (controlled model, 100 shifts): one-sided p = share of shifts with coefficient <= observed")
for v in obs:
    a = np.array(null[v]); L.append(f"  {v}: observed {obs[v]:+.3f}; null mean {a.mean():+.3f} [{np.percentile(a, 2.5):+.3f}, {np.percentile(a, 97.5):+.3f}]; p={(np.sum(a <= obs[v]) + 1) / (NSH + 1):.3f}")
pd.DataFrame(out).to_csv(f"{C.RES}/rem_artifacts.csv", index=False); open(f"{C.RES}/rem_artifacts_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
