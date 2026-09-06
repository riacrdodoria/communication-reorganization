"""T4 - Timing within the event: pre-onset vs onset vs post-onset socioemotional density, plus a
circular-shift null (METHODS.md sec.6 convention). RESOLUTION CAVEAT (disclosed, not hidden): the
coded content categories are only available at the established 90 s window grain, coarser than the
+/-30 s scale used for second-resolution metrics elsewhere in this program (e.g. topic-boundary
Delta-entropy in Study 6, which uses per-second RMSE/entropy). There is no finer-grained coding to
draw on, so "before/at/after" here means the window immediately preceding the event's onset window,
the onset window itself, and the window immediately following - explicitly reported at this grain,
not silently presented as +/-30 s precision."""
import glob, os, json
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

LSH = os.path.expanduser("~/lsh-work")
COD2 = f"{LSH}/data/codebooks2"
ACT4 = f"{LSH}/data/act4teams"
EVENTS_CSV = f"{LSH}/study9_initiators/data/events_initiators.csv"
OUT = os.path.dirname(__file__) + "/../data"
W = 90
N_NULL = 2000
rng = np.random.default_rng(1200)

POSITIVE = ["bsolid", "btension", "bagree", "pos"]
NEGATIVE = ["bdisagree", "btensh", "bantag", "neg"]
BALES_CATS = ["bsolid", "btension", "bagree", "bdisagree", "btensh", "bantag"]


def load_cb(folder):
    d = {}
    for f in glob.glob(f"{folder}/*_passA.json"):
        mid = os.path.basename(f).replace("_passA.json", "")
        d[mid] = {int(round(int(w["t"]) / 90) * 90): w for w in json.load(open(f))["windows"]}  # snap to the 90-s grid (one act4teams file is offset)
    return d


c2 = load_cb(COD2); c4 = load_cb(ACT4)
win = lambda s: int(s // W * W)


def composite_series(mid, cats):
    """Ordered (window_idx, density) series for a meeting, density = mean over available cats."""
    all_t = sorted(set(c2.get(mid, {})) | set(c4.get(mid, {})))
    series = {}
    for t in all_t:
        vals = []
        for cat in cats:
            cd = c2[mid] if cat in BALES_CATS else c4[mid]
            if t in cd and cat in cd[t]:
                vals.append(cd[t][cat])
        if vals:
            series[t] = np.mean(vals)
    return series


ev = pd.read_csv(EVENTS_CSV)


def pre_at_post_for_meeting(mid, onsets, series):
    """Mean pre/at/post density across this meeting's events, using its window series."""
    pre, at, post = [], [], []
    for o in onsets:
        t = win(o)
        if (t - W) in series and t in series and (t + W) in series:
            pre.append(series[t - W]); at.append(series[t]); post.append(series[t + W])
    if not pre:
        return None
    return np.mean(pre), np.mean(at), np.mean(post)


def run(cats, label):
    per_meeting = []
    for mid, g in ev.groupby("mid"):
        series = composite_series(mid, cats)
        if not series:
            continue
        r = pre_at_post_for_meeting(mid, g["event_onset_s"].tolist(), series)
        if r is not None:
            per_meeting.append((mid,) + r)
    if not per_meeting:
        print(f"  [{label}] insufficient data"); return None
    dfm = pd.DataFrame(per_meeting, columns=["mid", "pre", "at", "post"])
    obs_at_minus_pre = (dfm["at"] - dfm["pre"]).mean()
    obs_post_minus_at = (dfm["post"] - dfm["at"]).mean()
    p_pre_at = wilcoxon(dfm["at"], dfm["pre"], zero_method="wilcox").pvalue if len(dfm) >= 8 else np.nan
    p_at_post = wilcoxon(dfm["post"], dfm["at"], zero_method="wilcox").pvalue if len(dfm) >= 8 else np.nan

    # circular-shift null: rotate each meeting's window series by a random offset, keep same event
    # onset window indices, recompute the mean(at-pre) / mean(post-at) statistics, repeat N_NULL times
    null_at_minus_pre = np.empty(N_NULL); null_post_minus_at = np.empty(N_NULL)
    series_by_mid = {mid: composite_series(mid, cats) for mid in dfm["mid"]}
    onsets_by_mid = {mid: g["event_onset_s"].tolist() for mid, g in ev.groupby("mid") if mid in series_by_mid}
    for i in range(N_NULL):
        vals_ap, vals_pa = [], []
        for mid in dfm["mid"]:
            series = series_by_mid[mid]
            ts = sorted(series); n = len(ts)
            shift = rng.integers(1, n)
            shifted = {ts[(k + shift) % n]: series[ts[k]] for k in range(n)}
            r = pre_at_post_for_meeting(mid, onsets_by_mid[mid], shifted)
            if r is not None:
                vals_ap.append(r[1] - r[0]); vals_pa.append(r[2] - r[1])
        null_at_minus_pre[i] = np.mean(vals_ap) if vals_ap else np.nan
        null_post_minus_at[i] = np.mean(vals_pa) if vals_pa else np.nan
    # Phipson & Smyth (2010): (b+1)/(N+1); never reported as 0
    p_null_ap = (np.nansum(np.abs(null_at_minus_pre) >= abs(obs_at_minus_pre)) + 1) / (N_NULL + 1)
    p_null_pa = (np.nansum(np.abs(null_post_minus_at) >= abs(obs_post_minus_at)) + 1) / (N_NULL + 1)

    print(f"  [{label}]  n_meetings={len(dfm)}")
    print(f"    pre={dfm['pre'].mean():.4f}  at={dfm['at'].mean():.4f}  post={dfm['post'].mean():.4f}")
    fp = lambda p: (f"p<{1/N_NULL:.4f}" if p < 1/N_NULL else f"p={p:.4f}")  # null p floored at 1/N_NULL
    print(f"    at-pre = {obs_at_minus_pre:+.4f}  Wilcoxon p={p_pre_at:.4f}  circular-shift-null {fp(p_null_ap)}")
    print(f"    post-at = {obs_post_minus_at:+.4f}  Wilcoxon p={p_at_post:.4f}  circular-shift-null {fp(p_null_pa)}")
    return dict(label=label, n=len(dfm), pre=dfm["pre"].mean(), at=dfm["at"].mean(), post=dfm["post"].mean(),
                at_minus_pre=obs_at_minus_pre, p_at_minus_pre=p_pre_at, p_null_at_minus_pre=p_null_ap,
                post_minus_at=obs_post_minus_at, p_post_minus_at=p_at_post, p_null_post_minus_at=p_null_pa)


print("=" * 90); print("T4 — Timing within the event window (pre-onset / onset / post-onset), window-grain")
print("=" * 90)
results = []
for cats, label in [(POSITIVE, "positive composite"), (NEGATIVE, "negative composite"),
                     (["bagree"], "bagree"), (["pos"], "pos (act4teams)"), (["bsolid"], "bsolid")]:
    r = run(cats, label)
    if r:
        results.append(r)

pd.DataFrame(results).to_csv(f"{OUT}/socioemotional_timing.csv", index=False)
print(f"\nwrote {OUT}/socioemotional_timing.csv")
