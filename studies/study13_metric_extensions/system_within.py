"""Item 1b. The Gorman & Wiltshire (2024) systems WITHIN meetings. Each meeting is cut into 10-min segments (step 5 min).
In each segment the %MaxEnt series (60-s window, 1-s step) is tested for periodicity with periods 1-5 min against 100
surrogates that shuffle the order of team-state runs inside that segment (same window, same run lengths). Segments are
also tested for 'attractor strength': the lag-30 s autocorrelation of the entropy series versus the same surrogates
(higher than null = the series returns less quickly, i.e., weaker restoring force).
Segment class: I = not periodic; II = periodic with the same dominant period (within 25%) as the previous segment that
was periodic; III = periodic otherwise (periodicity switches on, or its period changes).
Each segment is labeled with its majority L10 stage and its event count. Analyses: class shares by stage; event rate
by class (Wilcoxon within meeting); class transitions at stage onsets.
Output: results/system_within_segments.csv, results/system_within_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.signal import welch
sys.path.insert(0, os.path.dirname(__file__)); import common as C
from typology import entropy_series, shuffled
rng = np.random.default_rng(31); SEG = 600; STEP = 300; NS = 100; PMIN, PMAX = 60, 300; HZ = 2

def psd(x, nps):
    x = x - np.polyval(np.polyfit(np.arange(x.size), x, 1), np.arange(x.size)); return welch(x, fs=1.0, nperseg=nps)

def ac(x, lag=30):
    x = x - x.mean(); return np.corrcoef(x[:-lag], x[lag:])[0, 1] if x.std() > 0 else np.nan

E = C.events(); rows = []
for mid in C.meetings():
    st, nsp = C.team_state(mid); ev = E[E.mid == mid].event_onset_s.to_numpy(); prev_period = None
    T = st.size / HZ
    for s0 in np.arange(0, T - SEG + 1, STEP):
        a, b = int(s0 * HZ), int((s0 + SEG) * HZ); seg = st[a:b]
        if len(np.unique(seg)) < 2: continue
        x = entropy_series(seg, nsp); nps = min(x.size, 256); f, P = psd(x, nps); band = (f >= 1 / PMAX) & (f <= 1 / PMIN)
        sur = [entropy_series(shuffled(seg), nsp) for _ in range(NS)]
        PS = np.array([psd(s, nps)[1] for s in sur]); ref = PS.mean(0)
        stat = (P[band] / ref[band]).max(); null = (PS[:, band] / ref[band]).max(1); p = (np.sum(null >= stat) + 1) / (NS + 1)
        period = 1 / f[band][np.argmax(P[band] / ref[band])]
        acx = ac(x); acn = np.array([ac(s) for s in sur]); p_ac = (np.sum(acn >= acx) + 1) / (NS + 1)
        if p >= .05: cls = "I"
        elif prev_period is not None and abs(period - prev_period) / prev_period <= .25: cls = "II"
        else: cls = "III"
        if p < .05: prev_period = period
        mid_s = s0 + SEG / 2; stage = C.stage_of_seconds(mid, np.array([mid_s]))[0]
        stages_in = C.stage_of_seconds(mid, np.arange(s0, s0 + SEG, 10)); maj = pd.Series(stages_in).mode()[0]
        n_ev = int(((ev >= s0) & (ev < s0 + SEG)).sum())
        rows.append(dict(mid=mid, team=C.team(mid), s0=s0, cls=cls, p_periodic=p, period_s=period, ac30=acx, ac30_null=acn.mean(), p_ac=p_ac,
                         stage_mid=stage, stage_major=maj, n_stage_changes=int((pd.Series(stages_in) != pd.Series(stages_in).shift()).sum() - 1), n_events=n_ev,
                         mean_entropy=x.mean(), sd_entropy=x.std()))
    print(mid, pd.Series([r["cls"] for r in rows if r["mid"] == mid]).value_counts().to_dict(), flush=True)
D = pd.DataFrame(rows); D.to_csv(f"{C.RES}/system_within_segments.csv", index=False)
D["stage_group"] = np.where(D.stage_major.isin(list(C.REVIEW)), "review", np.where(D.stage_major == "ids", "IDS", np.where(D.stage_major.isin(["segue", "headlines", "conclude"]), "open/close", "pre")))
L = [f"Segments: {len(D)} (10 min, step 5 min) in 34 meetings", "Class shares overall:", D.cls.value_counts(normalize=True).round(3).to_string(), "",
     "Class shares by stage group (rows sum to 1):", pd.crosstab(D.stage_group, D.cls, normalize="index").round(3).to_string(), "",
     "Events per segment by class:", D.groupby("cls").n_events.agg(["mean", "count"]).round(2).to_string(), "",
     f"Segments with weaker restoring force than shuffled (lag-30 s AC above null, p<.05): {int((D.p_ac<.05).sum())}/{len(D)}; mean AC obs {D.ac30.mean():.3f} vs null {D.ac30_null.mean():.3f}"]
d_ev = []
for mid, g in D.groupby("mid"):
    a = g[g.cls != "I"].n_events.mean(); b = g[g.cls == "I"].n_events.mean()
    if not np.isnan(a) and not np.isnan(b): d_ev.append(a - b)
p, n = C.wilcoxon_p(d_ev); L.append(f"Within meeting, events per segment periodic (II+III) minus non-periodic (I): mean {np.mean(d_ev):+.2f}, Wilcoxon p={p:.3f}, n={n}")
D["changes"] = D.n_stage_changes > 0
L.append("Class shares, segments that contain a stage change vs not:"); L.append(pd.crosstab(D.changes, D.cls, normalize="index").round(3).to_string())
open(f"{C.RES}/system_within_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
