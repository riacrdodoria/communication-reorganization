"""Shared loaders for Study 13 (metric extensions). Everything numeric; transcripts are read locally only.
Substrate: data/metrics_gorman_l8 (standard team-state series reconstructed with word-timed durations)."""
import os, re, json, glob, unicodedata, numpy as np, pandas as pd

L = os.path.expanduser("~/lsh-work")
GM = f"{L}/data/metrics_gorman_l8"; TXT = f"{L}/data/text_startup"
RES = f"{L}/study13_metric_extensions/results"; os.makedirs(RES, exist_ok=True)
STAGES = ["segue", "scorecard", "rock_review", "headlines", "todo", "ids", "conclude"]
REVIEW = {"scorecard", "rock_review", "todo"}

def meetings():
    return sorted(os.path.basename(f).replace("_gorman.csv", "") for f in glob.glob(f"{GM}/*_gorman.csv"))

def team(mid): return "A" if "startup_a" in mid else "B"

def week_map():
    m = meetings(); out = {}
    for t in "AB":
        ms = sorted(x for x in m if team(x) == t)
        for i, x in enumerate(ms): out[x] = i + 1
    return out

def metrics(mid): return pd.read_csv(f"{GM}/{mid}_gorman.csv")

def transcript(mid):
    tx = pd.read_csv(f"{TXT}/{mid}_transcript.csv")
    tx["onset_seconds"] = pd.to_numeric(tx.onset_seconds, errors="coerce")
    return tx.dropna(subset=["onset_seconds", "speaker_id"]).reset_index(drop=True)

_ROLES = None
def roles(mid):
    global _ROLES
    if _ROLES is None: _ROLES = pd.read_csv(f"{L}/study9_initiators/data/speaker_roles_verified.csv")
    r = _ROLES[_ROLES.mid == mid]
    return {str(a): b for a, b in zip(r.raw_id.astype(str), r.role)}

def events():
    e = pd.read_csv(f"{L}/study9_initiators/data/events_initiators.csv")
    return e

def episode_bounds(mid):
    ec = pd.read_csv(f"{L}/episode_codes.csv", usecols=["mid", "sec_start"])
    return np.sort(ec[ec.mid == mid].sec_start.to_numpy(float))[1:]  # drop the meeting start

def _norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower()); s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()

def stage_segments(mid):
    """[(stage, start_s, end_s)] from the quote-anchored L10 annotations (same rule as l10_analysis.py)."""
    f = f"{L}/data/l10_stages/{mid}.json"
    if not os.path.exists(f): return []
    d = json.load(open(f)); tx = pd.read_csv(f"{TXT}/{mid}_transcript.csv")
    on = pd.to_numeric(tx.onset_seconds, errors="coerce").to_numpy(); ntx = [_norm(t) for t in tx.text]
    seg = []; prev = 0
    for st in d["stages"]:
        q = _norm(st["quote"])[:60]; idx = None
        for i in range(prev, len(ntx)):
            if q and q in ntx[i]: idx = i; break
        if idx is None:
            for i in range(len(ntx)):
                if q and q in ntx[i]: idx = i; break
        if idx is not None: seg.append((st["name"], float(on[idx]))); prev = idx + 1
    end = float(np.nanmax(on)) + 5
    return [(n, s, seg[k + 1][1] if k + 1 < len(seg) else end) for k, (n, s) in enumerate(seg)]

def stage_of_seconds(mid, seconds):
    lab = np.array(["pre"] * len(seconds), dtype=object)
    for n, s0, s1 in stage_segments(mid):
        lab[(seconds >= s0) & (seconds < s1)] = n
    return lab

def team_state(mid):
    """2 Hz bitmask team-state series, identical to gorman_reimpl.build_states."""
    import sys; sys.path.insert(0, L); import gorman_reimpl as G
    df = pd.read_csv(f"{TXT}/{mid}_transcript.csv"); s, n = G.build_states(df); return s, n

def floor_holder_1hz(mid):
    """1 Hz series of the most recent utterance onset's speaker role (onset-based floor holder)."""
    tx = transcript(mid); R = roles(mid); T = int(np.ceil(tx.onset_seconds.max())) + 1
    lab = np.array([None] * T, dtype=object); cur = None; j = 0
    on = tx.onset_seconds.to_numpy(); sp = tx.speaker_id.astype(str).to_numpy()
    for t in range(T):
        while j < len(on) and on[j] <= t: cur = R.get(sp[j], "OTHER"); j += 1
        lab[t] = cur
    return lab

def wilcoxon_p(x):
    from scipy.stats import wilcoxon
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return (wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan), len(x)
