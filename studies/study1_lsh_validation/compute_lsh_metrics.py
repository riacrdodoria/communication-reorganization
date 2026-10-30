#!/usr/bin/env python3
"""Pure Last-Speaker-Holds metrics for the 34 meetings (onset-only substrate).
State at each 2 Hz sample = the speaker whose utterance onset was most recent (holds until the next onset).
No synthesized durations, no overlaps, no empty state. Window 60 s, step 1 s, %DET L_min = 8, RMSE by the
method of analogues (eps 3, h 20): same parameters as data/metrics_gorman_l8.
Writes data/metrics_lsh_l8/<mid>_lsh.csv (second, entropy_g, det_g, rmse_g) and a comparison table against
the published metrics: study1_lsh_validation/results/corpus_lsh_pure_vs_published.csv."""
import os, sys, glob, numpy as np, pandas as pd
from scipy.stats import pearsonr
sys.path.insert(0, os.path.expanduser("~/lsh-work"))
import gorman_reimpl as G
from importlib import util
spec = util.spec_from_file_location("ar", os.path.expanduser("~/lsh-work/study1_lsh_validation/lsh_convergent_current_params.py"))
src = open(spec.origin).read().split("inv = pd.read_csv")[0]; ns = {}; exec(src, ns)
det_fast, events, overlap, rr = ns["det_fast"], ns["events"], ns["overlap"], ns["r"]
OUTD = os.path.expanduser("~/lsh-work/data/metrics_lsh_l8"); os.makedirs(OUTD, exist_ok=True)

def build_lsh(df):
    d = df.dropna(subset=["onset_seconds", "speaker_id"]).sort_values("onset_seconds")
    sp = sorted(int(s) for s in d.speaker_id.unique()); idx = {s: i + 1 for i, s in enumerate(sp)}
    on = d.onset_seconds.to_numpy(float); who = np.array([idx[int(s)] for s in d.speaker_id])
    nt = int(np.ceil(on.max() / G.DT)) + 1; state = np.zeros(nt, dtype=np.int64)
    starts = np.floor(on / G.DT).astype(int)
    for k in range(len(on)):
        a = starts[k]; b = starts[k + 1] if k + 1 < len(on) else nt
        state[a:max(b, a + 1)] = who[k]
    first = starts[0]; return state[first:], len(sp)

def metrics(state, nsp):
    w = int(G.WIN_S / G.DT); half = w // 2; step = int(G.STEP_S / G.DT); maxbits = np.log2(nsp)
    secs, ent, det = [], [], []
    for c in range(half, state.size - half, step):
        seg = state[c - half:c + half + 1]
        _, cnt = np.unique(seg, return_counts=True); p = cnt / cnt.sum()
        secs.append(round(c * G.DT)); ent.append(100 * (-(p * np.log2(p)).sum()) / maxbits); det.append(det_fast(seg, (8,))[8])
    det = np.array(det); return pd.DataFrame({"second": secs, "entropy_g": ent, "det_g": det, "rmse_g": G.rmse_analogues(det)})

rows = []
for f in sorted(glob.glob(os.path.expanduser("~/lsh-work/data/text_startup/*_transcript.csv"))):
    mid = os.path.basename(f).replace("_transcript.csv", "")
    df = pd.read_csv(f); state, nsp = build_lsh(df); out = metrics(state, nsp)
    out.to_csv(f"{OUTD}/{mid}_lsh.csv", index=False)
    pub = pd.read_csv(os.path.expanduser(f"~/lsh-work/data/metrics_gorman_l8/{mid}_gorman.csv"))
    m = pd.merge(out, pub, on="second", suffixes=("_lsh", "_pub"))
    ea, eb = events(pub.rmse_g.to_numpy()), events(out.rmse_g.to_numpy()); oa, ob = overlap(ea, eb)
    rows.append(dict(mid=mid, n_speakers=nsp, r_entropy=rr(m.entropy_g_pub.to_numpy(), m.entropy_g_lsh.to_numpy()), r_det=rr(m.det_g_pub.to_numpy(), m.det_g_lsh.to_numpy()),
                     r_rmse=rr(m.rmse_g_pub.to_numpy(), m.rmse_g_lsh.to_numpy()), n_events_pub=len(ea), n_events_lsh=len(eb), events_pub_matched=oa, events_lsh_matched=ob,
                     mean_ent_pub=pub.entropy_g.mean(), mean_ent_lsh=out.entropy_g.mean(), mean_det_pub=pub.det_g.mean(), mean_det_lsh=out.det_g.mean()))
    print(f"{mid}: r_ent={rows[-1]['r_entropy']:.3f} r_det={rows[-1]['r_det']:.3f} r_rmse={rows[-1]['r_rmse']:.3f} events pub/lsh {len(ea)}/{len(eb)} matched {oa:.2f}/{ob:.2f} | mean ent {pub.entropy_g.mean():.1f}->{out.entropy_g.mean():.1f} det {pub.det_g.mean():.1f}->{out.det_g.mean():.1f}", flush=True)
T = pd.DataFrame(rows); T.to_csv(os.path.expanduser("~/lsh-work/study1_lsh_validation/results/corpus_lsh_pure_vs_published.csv"), index=False)
print("\nSUMMARY pure LSH vs published (34): median r entropy %.3f det %.3f rmse %.3f | events matched pub %.2f lsh %.2f | total events pub %d lsh %d | between-meeting r ent %.3f det %.3f" % (
    T.r_entropy.median(), T.r_det.median(), T.r_rmse.median(), T.events_pub_matched.mean(), T.events_lsh_matched.mean(), T.n_events_pub.sum(), T.n_events_lsh.sum(),
    pearsonr(T.mean_ent_pub, T.mean_ent_lsh)[0], pearsonr(T.mean_det_pub, T.mean_det_lsh)[0]))
