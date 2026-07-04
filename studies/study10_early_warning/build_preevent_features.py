"""T1 - Pre-event vs matched-baseline window features.

For every reorganization event (same detector as Studies 2/6/7/9: RMSE > mean+2.33 SD per meeting,
contiguous seconds clustered with an 8s gap rule), extract 6 features over the [-W, 0) s window
immediately BEFORE the event onset (default W=60; T4 reruns at W=30/90). For each event, 3 seeded
baseline windows are matched within the same meeting: same EOS L10 stage where possible, and the
baseline's own pseudo-onset is >=90s from every event onset in that meeting (so its own [-W,0) window
cannot itself overlap an event).

Features (all computed strictly from seconds/utterances BEFORE the window's end time - no information
at or after that time is used anywhere in this script):
  entropy_slope   - OLS slope of entropy_g vs time across the W per-second points in the window.
  det_slope       - same for det_g.
  switch_rate     - speaker switches per minute among utterances starting in the window.
  turnlen_trend   - OLS slope of per-utterance word count vs utterance order within the window.
  question_density- fraction of utterances in the window containing '?'.
  gap_trend       - OLS slope of inter-utterance silence gaps vs time within the window.

Output: preevent_features.csv (label=1 event-pre / 0 baseline; window_s = W)."""
import glob, os, json, re, unicodedata, sys
import numpy as np, pandas as pd

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
TXT = f"{LSH}/data/text_startup"
EP = pd.read_csv(f"{LSH}/episode_codes.csv")
TCRIT = 2.33
N_BASELINE = 3
MIN_SEP_FROM_EVENT = 90  # s, baseline pseudo-onset must be this far from every event onset
SEED = 10


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ?]", " ", s)).strip()


def l10_stage_bounds(mid):
    """Return [(stage_name, start_s, end_s), ...] for a meeting, or [] if unavailable."""
    f = f"{LSH}/data/l10_stages/{mid}.json"
    tp = f"{TXT}/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)):
        return []
    d = json.load(open(f)); tx = pd.read_csv(tp)
    on = pd.to_numeric(tx.onset_seconds, errors="coerce").to_numpy()
    nt = [norm(t) for t in tx.text]
    seg = []; prev = 0
    for st in d["stages"]:
        q = norm(st["quote"])[:60]; idx = None
        for i in range(prev, len(nt)):
            if q and q in nt[i]: idx = i; break
        if idx is None:
            for i in range(len(nt)):
                if q and q in nt[i]: idx = i; break
        if idx is not None:
            seg.append((st["name"], float(on[idx]))); prev = idx + 1
    if not seg:
        return []
    bounds = [s[1] for s in seg] + [float(np.nanmax(on)) + 5]
    return [(seg[k][0], seg[k][1], bounds[k + 1]) for k in range(len(seg))]


def parse_date_team(mid):
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})(startup_[ab])", mid)
    y, mo, d, team = m.groups()
    return int(f"{y}{mo}{d}"), team


def window_features(t_end, W, sec, ent, det, onset_all, speak_all, text_all, nw_all, end_all):
    """Features over [t_end-W, t_end). Strictly excludes t_end itself and anything after."""
    lo = t_end - W
    m_sec = (sec >= lo) & (sec < t_end)
    if m_sec.sum() < max(10, W // 3):
        return None
    tt = sec[m_sec]
    def slope(y):
        y = y[np.isfinite(y)]
        if len(y) < 5: return np.nan
        x = np.arange(len(y), dtype=float)
        return float(np.polyfit(x, y, 1)[0])
    entropy_slope = slope(ent[m_sec])
    det_slope = slope(det[m_sec])

    m_utt = (onset_all >= lo) & (onset_all < t_end)
    if m_utt.sum() < 2:
        switch_rate = np.nan; turnlen_trend = np.nan; question_density = np.nan; gap_trend = np.nan
    else:
        sp = speak_all[m_utt]; txts = text_all[m_utt]; nw = nw_all[m_utt]; on = onset_all[m_utt]; ed = end_all[m_utt]
        order = np.argsort(on)
        sp, txts, nw, on, ed = sp[order], txts[order], nw[order], on[order], ed[order]
        n_switch = int(np.sum(sp[1:] != sp[:-1]))
        dur_min = W / 60.0
        switch_rate = n_switch / dur_min
        turnlen_trend = slope(nw.astype(float))
        question_density = float(np.mean(["?" in t for t in txts]))
        if len(on) >= 3:
            gaps = on[1:] - ed[:-1]
            gap_trend = slope(gaps)
        else:
            gap_trend = np.nan
    return dict(entropy_slope=entropy_slope, det_slope=det_slope, switch_rate=switch_rate,
                turnlen_trend=turnlen_trend, question_density=question_density, gap_trend=gap_trend)


def build(W, out_path, seed=SEED):
    rng = np.random.default_rng(seed)
    rows = []
    for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
        mid = os.path.basename(f).replace("_gorman.csv", "")
        date, team = parse_date_team(mid)
        tp = f"{TXT}/{mid}_transcript.csv"
        if not os.path.exists(tp):
            continue
        tx = pd.read_csv(tp)
        onset_all = pd.to_numeric(tx.onset_seconds, errors="coerce").to_numpy()
        speak_all = tx.speaker_id.astype(str).to_numpy()
        text_all = tx.text.astype(str).to_numpy()
        nw_all = np.array([max(1, len(t.split())) for t in text_all])
        end_all = onset_all + 0.5 * nw_all
        ok = np.isfinite(onset_all)
        onset_all, speak_all, text_all, nw_all, end_all = (a[ok] for a in (onset_all, speak_all, text_all, nw_all, end_all))
        order = np.argsort(onset_all)
        onset_all, speak_all, text_all, nw_all, end_all = (a[order] for a in (onset_all, speak_all, text_all, nw_all, end_all))

        g = pd.read_csv(f)
        sec = g.second.to_numpy(float)
        ent = g.entropy_g.to_numpy(float); det = g.det_g.to_numpy(float); rm = g.rmse_g.to_numpy(float)
        okm = np.isfinite(rm)
        if okm.sum() < 60:
            continue
        rmean, rsd = np.nanmean(rm[okm]), np.nanstd(rm[okm])
        peak = rm > rmean + TCRIT * rsd
        evsec = sec[okm][peak[okm]]
        t_min, t_max = float(np.nanmin(sec)), float(np.nanmax(sec))

        # cluster consecutive event-seconds into discrete events (gap>8s = new event)
        events = []; cur = []
        for s in evsec:
            if cur and s - cur[-1] > 8:
                events.append(cur); cur = []
            cur.append(s)
        if cur: events.append(cur)
        onsets = [float(ev[0]) for ev in events]
        if not onsets:
            continue

        stages = l10_stage_bounds(mid)
        def stage_at(t):
            for name, s0, s1 in stages:
                if s0 <= t < s1: return name
            return None

        # candidate baseline pseudo-onsets: any second >= W (so pre-window fits) and <= t_max,
        # at least MIN_SEP_FROM_EVENT from every event onset
        cand_pool = sec[(sec >= W) & (sec <= t_max)]
        cand_pool = cand_pool[np.array([min(abs(c - o) for o in onsets) >= MIN_SEP_FROM_EVENT for c in cand_pool])]

        for eidx, onset_s in enumerate(onsets):
            feat = window_features(onset_s, W, sec, ent, det, onset_all, speak_all, text_all, nw_all, end_all)
            if feat is None:
                continue
            ev_stage = stage_at(onset_s)
            row = dict(mid=mid, team=team, date=date, event_id=eidx, onset_s=onset_s, window_s=W,
                       label=1, l10_stage=ev_stage, **feat)
            rows.append(row)

            # matched baselines: prefer same stage, else any candidate
            same_stage = cand_pool[np.array([stage_at(c) == ev_stage for c in cand_pool])] if ev_stage else np.array([])
            pool = same_stage if len(same_stage) >= N_BASELINE else cand_pool
            if len(pool) == 0:
                continue
            picks = rng.choice(pool, size=min(N_BASELINE, len(pool)), replace=False)
            for bidx, b in enumerate(picks):
                bfeat = window_features(float(b), W, sec, ent, det, onset_all, speak_all, text_all, nw_all, end_all)
                if bfeat is None:
                    continue
                rows.append(dict(mid=mid, team=team, date=date, event_id=eidx, onset_s=float(b), window_s=W,
                                  label=0, l10_stage=stage_at(float(b)), **bfeat))

    D = pd.DataFrame(rows)
    D.to_csv(out_path, index=False)
    print(f"W={W}s: wrote {out_path}  ({len(D)} rows: {int((D.label==1).sum())} event-pre, "
          f"{int((D.label==0).sum())} baseline; {D.mid.nunique()} meetings)")
    return D


if __name__ == "__main__":
    OUTDIR = f"{os.path.dirname(__file__)}/../data"
    os.makedirs(OUTDIR, exist_ok=True)
    build(60, f"{OUTDIR}/preevent_features.csv")       # primary
    build(30, f"{OUTDIR}/preevent_features_w30.csv")    # T4 sensitivity
    build(90, f"{OUTDIR}/preevent_features_w90.csv")    # T4 sensitivity
