"""Item 7. Collective rhythm and intermittency. Burstiness B = (sd - mean)/(sd + mean) and memory coefficient M
(correlation of consecutive intervals) of (a) utterance inter-onset intervals and (b) inter-event intervals; Allan
factor of event counts at T = 30..600 s. Null for events: event times redrawn uniformly within the meeting (1000x,
same count), keeping the event-free margins. Output: results/rhythm_meeting.csv, results/rhythm_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(7); TS = [30, 60, 120, 300, 600]

def BM(t):
    iv = np.diff(np.sort(t)); iv = iv[iv > 0]
    if iv.size < 4: return np.nan, np.nan
    B = (iv.std() - iv.mean()) / (iv.std() + iv.mean()); M = np.corrcoef(iv[:-1], iv[1:])[0, 1]
    return B, M

def allan(t, T, t0, t1):
    edges = np.arange(t0, t1 + T, T); c = np.histogram(t, edges)[0]
    if c.size < 4 or c.mean() == 0: return np.nan
    return np.mean(np.diff(c) ** 2) / (2 * c.mean())

E = C.events(); W = C.week_map(); rows = []
for mid in C.meetings():
    tx = C.transcript(mid); on = tx.onset_seconds.to_numpy(float); ev = E[E.mid == mid].event_onset_s.to_numpy(float)
    sec = C.metrics(mid).second; t0, t1 = sec.min(), sec.max()
    Bu, Mu = BM(on); Be, Me = BM(ev)
    null = np.array([BM(rng.uniform(t0, t1, ev.size)) for _ in range(1000)])
    af = {T: allan(ev, T, t0, t1) for T in TS}
    afn = {T: np.nanmean([allan(rng.uniform(t0, t1, ev.size), T, t0, t1) for _ in range(300)]) for T in TS}
    rows.append(dict(mid=mid, team=C.team(mid), week=W[mid], n_events=ev.size, B_utt=Bu, M_utt=Mu, B_ev=Be, M_ev=Me,
                     B_ev_null=np.nanmean(null[:, 0]), p_B_ev=(np.sum(null[:, 0] >= Be) + 1) / 1001,
                     **{f"AF_{T}": af[T] for T in TS}, **{f"AFnull_{T}": afn[T] for T in TS}))
    print(mid, f"B_utt={Bu:.2f} B_ev={Be:.2f} (null {np.nanmean(null[:,0]):.2f}, p={rows[-1]['p_B_ev']:.3f})", flush=True)
T = pd.DataFrame(rows); T.to_csv(f"{C.RES}/rhythm_meeting.csv", index=False)
L = [f"Utterance onsets: B mean {T.B_utt.mean():.3f} (range {T.B_utt.min():.2f}-{T.B_utt.max():.2f}); memory M {T.M_utt.mean():+.3f}",
     f"Events: B mean {T.B_ev.mean():.3f} vs uniform null {T.B_ev_null.mean():.3f}; meetings with p<.05: {int((T.p_B_ev<.05).sum())}/34; Wilcoxon B-null p={C.wilcoxon_p(T.B_ev-T.B_ev_null)[0]:.2e}; memory M {T.M_ev.mean():+.3f} (Wilcoxon vs 0 p={C.wilcoxon_p(T.M_ev)[0]:.3f})"]
for Tt in TS: L.append(f"Allan factor T={Tt:>3}s: observed {T[f'AF_{Tt}'].mean():.2f} vs null {T[f'AFnull_{Tt}'].mean():.2f} (Wilcoxon p={C.wilcoxon_p(T[f'AF_{Tt}']-T[f'AFnull_{Tt}'])[0]:.2e})")
for t, g in T.groupby("team"):
    L.append(f"Team {t}: event burstiness vs week tau={kendalltau(g.week, g.B_ev)[0]:+.2f} (p={kendalltau(g.week, g.B_ev)[1]:.2f}); utterance B vs week tau={kendalltau(g.week, g.B_utt)[0]:+.2f} (p={kendalltau(g.week, g.B_utt)[1]:.2f})")
open(f"{C.RES}/rhythm_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
