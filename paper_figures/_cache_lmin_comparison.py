"""Cache builder (not a paper figure itself): recomputes %DET at L_min=2 (old, saturated) and
L_min=8 (current, de-saturated) pooled across all meeting-seconds, for the Fig1 Panel B inset.
Reuses gorman_reimpl.py's build_states/det_window exactly as reproduce_two_regimes.py does, but
only computes what the inset needs (no clustering/silhouette) and caches to disk."""
import glob, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/lsh-work"))
import gorman_reimpl as gr

OUT = os.path.dirname(__file__) + "/_cache_lmin_det.csv"
HZ = gr.HZ; WIN = gr.WIN_S * HZ; STEP = 8 * HZ
TXT = os.path.expanduser("~/lsh-work/data/text_startup")


def winmetrics(state, nsp):
    D2, D8 = [], []
    for a in range(0, len(state) - WIN, STEP):
        seg = state[a:a + WIN]
        D2.append(gr.det_window(seg, lmin=2)); D8.append(gr.det_window(seg, lmin=8))
    return np.array(D2), np.array(D8)


rows = []
for f in sorted(glob.glob(f"{TXT}/*_transcript.csv")):
    mid = os.path.basename(f).replace("_transcript.csv", "")
    try:
        df = pd.read_csv(f); st, nsp = gr.build_states(df)
    except Exception:
        continue
    if nsp < 2 or len(st) < WIN + 10:
        continue
    d2, d8 = winmetrics(st, nsp)
    for a, b in zip(d2, d8):
        rows.append((mid, a, b))
    print(f"  {mid}: {len(d2)} windows")

out = pd.DataFrame(rows, columns=["mid", "det_lmin2", "det_lmin8"])
out.to_csv(OUT, index=False)
print(f"wrote {OUT} ({len(out)} pooled windows)")
