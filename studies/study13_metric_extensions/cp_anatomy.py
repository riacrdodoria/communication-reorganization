"""What are the PELT change points of %MaxEnt, given that they are as numerous as in run-shuffled meetings and do not
align with stage or topic boundaries?
Per meeting: change points (cps) as in system_cuts.pelt; signed shift = mean %MaxEnt in (cp, cp+60] minus [cp-60, cp).
(1) Magnitude: |shift| at observed cps vs cps of 20 run-shuffled versions of the meeting. 'Strong' cps = |shift| above
    the 95th percentile of that meeting's shuffle cps.
(2) Anatomy (observed cps vs 1000 circular shifts of the same cps): within +/-15 s of the start or end of a long turn
    (one speaker holds the floor >= 30 s; turns = runs of one speaker's utterances, duration to the next speaker's onset);
    dominant floor holder (onset-based, 1 Hz) of the 60 s before vs after differs; dominant role after a downward cp.
(3) Alignment of all and of strong cps with RMSE events, stage boundaries and topic boundaries (mean distance vs circular).
(4) Content at cps: residual lexical novelty and topic entropy (content_windows.csv) within +/-15 s vs elsewhere.
(5) cps per 10 min by stage group.
Output: results/cp_anatomy_cps.csv, results/cp_anatomy_summary.txt"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as C
from typology import entropy_series, shuffled
from system_cuts import pelt, nearest
rng = np.random.default_rng(81); NSH = 20; NCIRC = 1000; HZ = 2
E = C.events(); CW = pd.read_csv(f"{C.RES}/content_windows.csv")

def shifts(x, cps_idx):
    return np.array([x[c:c + 60].mean() - x[max(0, c - 60):c].mean() for c in cps_idx])

def dominant(lab, a, b):
    s = pd.Series(lab[max(0, a):b]).dropna()
    return s.mode().iloc[0] if len(s) else None

rows = []; summ = []
for mid in C.meetings():
    st, nsp = C.team_state(mid); x = entropy_series(st, nsp); T = st.size / HZ
    ci = pelt(x); cps = ci + 30.0; sh = shifts(x, ci)
    nul = []
    for _ in range(NSH):
        xs = entropy_series(shuffled(st), nsp); cs = pelt(xs); nul += list(np.abs(shifts(xs, cs)))
    thr = np.percentile(nul, 95)
    # long turns
    tx = C.transcript(mid); sp = tx.speaker_id.astype(str).to_numpy(); on = tx.onset_seconds.to_numpy()
    k = np.concatenate(([True], sp[1:] != sp[:-1])); ts = on[k]; dur = np.diff(np.concatenate((ts, [on.max() + 5])))
    lt_b = np.concatenate((ts[dur >= 30], (ts + dur)[dur >= 30]))
    lab = C.floor_holder_1hz(mid)
    ev = E[E.mid == mid].event_onset_s.to_numpy(); sb = np.array([a for _, a, _ in C.stage_segments(mid)][1:]); eb = C.episode_bounds(mid)
    def feats(c):
        c = np.asarray(c); f = {}
        f["near_longturn"] = (nearest(c, lt_b) <= 15).mean() if lt_b.size else np.nan
        dch = []
        for t in c.astype(int):
            a, b = dominant(lab, t - 60, t), dominant(lab, t, t + 60); dch.append(a is not None and b is not None and a != b)
        f["dominant_change"] = np.mean(dch)
        for nm, B in [("event", ev), ("stage", sb), ("topic", eb)]: f[f"d_{nm}"] = nearest(c, B).mean() if B.size and c.size else np.nan
        return f
    fo = feats(cps); circ = [feats((cps + rng.uniform(0, T)) % T) for _ in range(200)]
    strong = cps[np.abs(sh) > thr]; fs = feats(strong) if strong.size else {}
    circ_s = [feats((strong + rng.uniform(0, T)) % T) for _ in range(200)] if strong.size else []
    stg = C.stage_of_seconds(mid, cps)
    for c, s, g in zip(cps, sh, stg):
        t = int(c); rows.append(dict(mid=mid, team=C.team(mid), cp=c, shift=s, strong=abs(s) > thr, stage=g,
                                     dom_before=dominant(lab, t - 60, t), dom_after=dominant(lab, t, t + 60),
                                     near_longturn=bool(lt_b.size and nearest(np.array([c]), lt_b)[0] <= 15)))
    rec = dict(mid=mid, n_cp=len(cps), n_strong=int(strong.size), abs_shift=np.abs(sh).mean(), abs_shift_null=np.mean(nul), thr=thr,
               dur_min=T / 60)
    for kk in fo:
        rec[kk] = fo[kk]; rec[kk + "_null"] = np.nanmean([c[kk] for c in circ])
        if fs: rec["S_" + kk] = fs[kk]; rec["S_" + kk + "_null"] = np.nanmean([c[kk] for c in circ_s])
    # content
    cw = CW[CW.mid == mid]; dc = nearest(cw.sec.to_numpy(), cps) if cps.size else np.full(len(cw), 1e9)
    for m in ["novelty_res", "topic_entropy_res"]:
        sd = cw[m].std(); rec[f"{m}_at_cp"] = (cw[m][dc <= 15].mean() - cw[m][dc > 45].mean()) / sd
    summ.append(rec)
    print(mid, f"cps {len(cps)} strong {strong.size} |shift| {np.abs(sh).mean():.2f}/{np.mean(nul):.2f} longturn {fo['near_longturn']:.2f}/{rec['near_longturn_null']:.2f} domchg {fo['dominant_change']:.2f}/{rec['dominant_change_null']:.2f}", flush=True)

P = pd.DataFrame(rows); S = pd.DataFrame(summ); P.to_csv(f"{C.RES}/cp_anatomy_cps.csv", index=False); S.to_csv(f"{C.RES}/cp_anatomy_meeting.csv", index=False)
w = lambda d: C.wilcoxon_p(d)[0]
L = [f"Change points: {S.n_cp.sum()} in 34 meetings; strong (|shift| > 95th pct of shuffle cps): {S.n_strong.sum()} ({S.n_strong.sum()/S.n_cp.sum():.1%}; 5% expected)",
     f"|shift| observed {S.abs_shift.mean():.2f} vs shuffle cps {S.abs_shift_null.mean():.2f} %MaxEnt (Wilcoxon p={w(S.abs_shift-S.abs_shift_null):.1e})", "",
     "Anatomy, all cps (observed vs circular shift):"]
for kk, lab_ in [("near_longturn", "within 15 s of a long-turn start/end"), ("dominant_change", "dominant floor holder changes"),
                 ("d_event", "mean distance to event (s)"), ("d_stage", "mean distance to stage boundary (s)"), ("d_topic", "mean distance to topic boundary (s)")]:
    L.append(f"  {lab_:<40} {S[kk].mean():.3f} vs {S[kk+'_null'].mean():.3f}  (Wilcoxon p={w(S[kk]-S[kk+'_null']):.1e})")
L.append("Anatomy, strong cps only:")
for kk, lab_ in [("near_longturn", "within 15 s of a long-turn start/end"), ("dominant_change", "dominant floor holder changes"),
                 ("d_event", "mean distance to event (s)"), ("d_stage", "mean distance to stage boundary (s)"), ("d_topic", "mean distance to topic boundary (s)")]:
    if "S_" + kk in S: L.append(f"  {lab_:<40} {S['S_'+kk].mean():.3f} vs {S['S_'+kk+'_null'].mean():.3f}  (Wilcoxon p={w(S['S_'+kk]-S['S_'+kk+'_null']):.1e})")
L.append("")
L.append(f"Share of cps near a long-turn boundary: all {P.near_longturn.mean():.3f}; strong {P[P.strong].near_longturn.mean():.3f}")
dn = P[P['shift'] < 0]; up = P[P['shift'] > 0]
L.append(f"Downward cps (entropy falls) {len(dn)}: dominant after = " + dn.dom_after.value_counts(normalize=True).round(3).to_dict().__str__())
L.append(f"Upward cps (entropy rises) {len(up)}: dominant before = " + up.dom_before.value_counts(normalize=True).round(3).to_dict().__str__())
L.append(f"Content at cps (standardized, +/-15 s vs > 45 s): novelty_res {S.novelty_res_at_cp.mean():+.3f} (p={w(S.novelty_res_at_cp):.1e}); topic_entropy_res {S.topic_entropy_res_at_cp.mean():+.3f} (p={w(S.topic_entropy_res_at_cp):.1e})")
P["grp"] = np.where(P.stage.isin(list(C.REVIEW)), "review", np.where(P.stage == "ids", "IDS", "other"))
L.append("cps by stage group (share of all cps): " + P.grp.value_counts(normalize=True).round(3).to_dict().__str__())
open(f"{C.RES}/cp_anatomy_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
