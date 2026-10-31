"""Moment atlas: a statistically defined sampling frame for the qualitative study (Paper 2). Times only, no text.
Per reorganization event: depth; agenda relation (anticipates an agenda onset by 0-90 s / within +/-30 s / interior);
aftershock (another event 30-75 s earlier) and precursor-of-aftershock; early-warning strength (Kendall tau of rolling
%DET variance over [-180, -30] s); return to an earlier subject at the event (C1 of content_dynamics2); lexical topic
mixing and novelty at the event; member questions in the 45 s after onset; floor state 60 s before and after.
Plus non-event moments: extended floor turns whose vocabulary was taken up by others with vs without a following event.
Strata (each ranked, top 10 per stratum, at most 2 per meeting for spread): see STRATA below.
Output: results/atlas_events.csv (all events with features), results/atlas_sample.csv (stratified sample),
results/atlas_summary.txt"""
import sys, os, json, numpy as np, pandas as pd
from scipy.stats import kendalltau
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
P = json.load(open(f"{CM.RES}/partitions_bounds.json")); EV = CM.events(); CW = pd.read_csv(f"{CM.RES}/content_windows.csv")
ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv"); TU = pd.read_csv(f"{CM.RES}/seqdyn_turns.csv"); T1 = pd.read_csv(f"{CM.RES}/floor_cycle_T1_turns.csv")
LLM = json.load(open(f"{CM.RES}/llm_topics_bounds.json")) if os.path.exists(f"{CM.RES}/llm_topics_bounds.json") else {}
def near(a, b): a = np.asarray(a); b = np.asarray(b); return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.full(a.size, 1e9)
rows = []
for m in CM.meetings():
    ev = EV[EV.mid == m].sort_values("event_onset_s"); on = ev.event_onset_s.to_numpy(); ag = np.array(P[m]["agenda"])
    det = CM.metrics(m).set_index("second").det_g; cw = CW[CW.mid == m]; st = ST[ST.mid == m].set_index("sec").state; tu = TU[TU.mid == m]
    for i, (t, dep, cls) in enumerate(zip(on, ev.depth, ev.event_class)):
        seg = det.reindex(np.arange(int(t) - 180, int(t) - 30)).interpolate(limit_direction="both").to_numpy()
        ew = np.nan
        if np.isfinite(seg).sum() > 100:
            res = seg - gaussian_filter1d(seg, 30); v = [res[k:k + 40].var() for k in range(0, res.size - 40, 2)]; ew = kendalltau(np.arange(len(v)), v)[0]
        ahead = ag - t; antic = np.any((ahead >= 0) & (ahead <= 90)) if ag.size else False; atag = (near([t], ag)[0] <= 30) if ag.size else False
        c = cw[np.abs(cw.sec - t) <= 5]
        rows.append(dict(mid=m, team=CM.team(m), onset_s=t, depth=dep, s7_class=cls,
                         agenda=("anticipates" if antic else ("at" if atag else "interior")),
                         aftershock=bool(i > 0 and 30 <= t - on[i - 1] <= 75), has_aftershock=bool(i + 1 < len(on) and 30 <= on[i + 1] - t <= 75),
                         early_warning_tau=ew, topic_mix=c.topic_entropy_res.mean() if len(c) else np.nan, novelty=c.novelty_res.mean() if len(c) else np.nan,
                         member_questions_45s=int(((tu.t > t) & (tu.t <= t + 45) & tu.question & (tu.role != "FACILITATOR") & (tu.role != "OTHER")).sum()),
                         floor_before=st.reindex([t - 60], method="nearest").iloc[0] if len(st) else None, floor_after=st.reindex([t + 30], method="nearest").iloc[0] if len(st) else None,
                         llm_topic_boundary=bool(m in LLM and near([t], LLM[m]["topic"])[0] <= 30)))
A = pd.DataFrame(rows)
for c in ["depth", "early_warning_tau", "topic_mix", "novelty"]: A[c + "_z"] = A.groupby("mid")[c].transform(lambda x: (x - x.mean()) / x.std())
A.to_csv(f"{CM.RES}/atlas_events.csv", index=False)
STRATA = {
    "anticipates agenda transition": (A.agenda == "anticipates", "depth_z"),
    "interior, deepest": (A.agenda == "interior", "depth_z"),
    "first of an aftershock pair": (A.has_aftershock, "depth_z"),
    "strong early warning": (A.early_warning_tau.notna(), "early_warning_tau_z"),
    "no early warning (control)": (A.early_warning_tau.notna(), None),
    "highest topic mixing": (A.topic_mix.notna(), "topic_mix_z"),
    "followed by member questions": (A.member_questions_45s >= 2, "depth_z"),
}
samp = []
for name, (mask, key) in STRATA.items():
    d = A[mask].copy()
    d = d.sort_values("early_warning_tau_z") if key is None else d.sort_values(key, ascending=False)
    d = d.groupby("mid").head(2).head(10); d["stratum"] = name; samp.append(d)
# non-event moments: long turns taken up, with vs without a following event
T1["integ"] = T1.uptake - T1.uptake_null; lt = T1[T1.long == 1].dropna(subset=["integ"])
for name, mask in [("long turn taken up, event follows", lt.event60 == 1), ("long turn taken up, no event", lt.event60 == 0)]:
    d = lt[mask].sort_values("integ", ascending=False).groupby("mid").head(2).head(10)
    samp.append(pd.DataFrame(dict(mid=d.mid, onset_s=d.te, stratum=name, team=d.mid.map(CM.team))))
S = pd.concat(samp, ignore_index=True)[["stratum", "mid", "team", "onset_s", "agenda", "depth", "early_warning_tau", "topic_mix", "member_questions_45s", "floor_before", "floor_after", "llm_topic_boundary"]]
S.to_csv(f"{CM.RES}/atlas_sample.csv", index=False)
L = [f"Events: {len(A)}. Agenda relation: " + A.agenda.value_counts(normalize=True).round(3).to_dict().__str__(),
     f"Aftershocks: {A.aftershock.mean():.3f} of events follow another within 30-75 s",
     "Depth by agenda relation (mean z): " + A.groupby("agenda").depth_z.mean().round(3).to_dict().__str__(),
     "Floor before -> after (share): " + pd.crosstab(A.floor_before, A.floor_after, normalize=True).round(3).to_string().replace("\n", " | "),
     f"Sample: {len(S)} moments in {S.mid.nunique()} meetings; per stratum " + S.stratum.value_counts().to_dict().__str__()]
open(f"{CM.RES}/atlas_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
