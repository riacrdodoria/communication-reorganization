"""T1 - Who initiates reorganization events? Build the per-event initiator table.

Reuses the established event definition (rmse_g > mean+2.33 SD, per meeting; contiguous seconds with
gap<=8s = one event) and the established boundary/class logic from Study 7 (reorg_signature.py):
TRANSITION = event center within +/-30s of a topic-episode start or EOS L10 stage onset; else
INTERIOR (further split into handoff/other by whether the dominant speaker changes pre->post).

Facilitator identification (corrected): per-meeting raw_speaker_id of the facilitator, verified against
the researcher's own retained name-labeled source transcripts (not published; raw speaker_id is a
per-meeting first-appearance index, not a stable cross-meeting identity, so it must be resolved per
meeting, not assumed constant). See facilitator_identification.md for the corrected numbers and the
prior (wrong) constant-id approach it replaces.

Three initiator definitions per event, all computed from raw utterance onset/speaker/text (no
audio, no new metrics):
  init_primary  = first speaker, among utterances starting in [onset-5s, onset+10s], who differs
                  from the DOMINANT speaker of the pre-window [onset-15s, onset) (by word count).
                  Falls back to init_floor if no such utterance exists (e.g. same speaker throughout).
  init_floor    = speaker holding the floor at the exact onset second (last utterance whose
                  [onset, onset+0.5*n_words) active interval covers onset; else nearest prior
                  utterance's speaker - same Last-Speaker-Holds convention used throughout this repo).
  init_question = first speaker, among utterances in [onset-5s, onset+10s], whose text contains '?'.
                  Null if no question in the window.

Speaker ids are pseudonymized per team as S1, S2, ... (numeric order of first appearance in that
meeting's transcript); the facilitator is additionally flagged 'L'. Output: events_initiators.csv."""
import glob, os, json, re, unicodedata
import numpy as np, pandas as pd
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))
from roles import role_map
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
import reorg_events as RE

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
TXT = f"{LSH}/data/text_startup"
EP = pd.read_csv(f"{LSH}/episode_codes.csv")
TCRIT = 2.33

# CORRECTED (was a hardcoded "2" for all 34 meetings): raw speaker_id is assigned per meeting by
# order of first appearance, so it is NOT a stable identifier across meetings and a single constant
# cannot be right for more than one meeting at a time. The facilitator's true raw_speaker_id per
# meeting is now read from data/facilitator_raw_id_verified.csv, cross-checked against the
# researcher's own retained (unpublished) name-labeled source transcripts - 100% internally
# consistent per meeting (every utterance attributed to the facilitator maps to a single raw
# speaker_id in that meeting). Distribution across the 34 meetings: raw id "1" in 23 meetings, "2"
# in 10, "3" in 1 - confirming the old constant ("2") was wrong in 24/34 meetings.
FACILITATOR_RAW_ID_BY_MID = pd.read_csv(f"{os.path.dirname(__file__)}/../data/facilitator_raw_id_verified.csv").set_index("mid")["facilitator_raw_id"].astype(str).to_dict()


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ?]", " ", s)).strip()


def l10_onsets(mid):
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
            seg.append(float(on[idx])); prev = idx + 1
    return seg


def parse_date_team(mid):
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})(startup_[ab])", mid)
    y, mo, d, team = m.groups()
    return int(f"{y}{mo}{d}"), team


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
    # speaker labels = verified per-meeting ROLES (persistent across meetings; no names). Replaces the
    # earlier S1..Sn pseudonyms, which were per-meeting first-appearance order and therefore not a person.
    pseudo = role_map(mid)
    assert all(s in pseudo for s in set(speak_all)), (mid, set(speak_all) - set(pseudo))
    facilitator_pseudo = "FACILITATOR"
    assert pseudo.get(FACILITATOR_RAW_ID_BY_MID.get(mid)) == facilitator_pseudo, mid

    g = pd.read_csv(f)
    sec = g.second.to_numpy(float)
    ent = g.entropy_g.to_numpy(float); det = g.det_g.to_numpy(float); rm = g.rmse_g.to_numpy(float)
    okm = np.isfinite(rm)
    if okm.sum() < 60:
        continue
    rmean, rsd = np.nanmean(rm[okm]), np.nanstd(rm[okm])
    bent = np.nanmean(ent[okm & (rm <= rmean + TCRIT * rsd)])  # interior/baseline entropy for depth
    peak = rm > rmean + TCRIT * rsd
    evsec = sec[okm][peak[okm]]
    tb = sorted(EP[EP.mid == mid].sec_start.tolist())
    lb = l10_onsets(mid)
    bd = sorted(set(tb) | set(lb))

    def dom_speaker(a, b):  # dominant speaker by word count in [a,b)
        m = (onset_all >= a) & (onset_all < b)
        if not m.any(): return None
        s = {}
        for sp, w in zip(speak_all[m], nw_all[m]): s[sp] = s.get(sp, 0) + w
        return max(s, key=s.get)

    def floor_speaker(t):  # LSH convention: last utterance active at/covering t
        m = (onset_all <= t) & (end_all > t)
        cand = np.where(m)[0]
        if len(cand): return speak_all[cand[-1]]
        prior = np.where(onset_all <= t)[0]
        return speak_all[prior[-1]] if len(prior) else None

    # cluster consecutive event-seconds into discrete events (gap>8s = new event), shared with Study 7
    events = RE.cluster_events(evsec)

    for ev in events:
        onset_s = float(ev[0])
        center = float(np.mean(ev))
        # 2026-09-05: event_class now uses the CANONICAL Study 7 rule (centre, ±30 s, turn-count dominance);
        # the earlier Study 9 rule (onset, ±15 s, word-count dominance) is kept as event_class_s9rule for sensitivity.
        ev_class, _, _ = RE.classify(ev, bd, onset_all, speak_all, nw_all)
        ev_class_s9, _, _ = RE.classify(ev, bd, onset_all, speak_all, nw_all, anchor="onset", window=15, weight="words")
        # depth: entropy at event window minus meeting interior baseline
        wmask = (sec >= onset_s) & (sec <= onset_s + 15)
        depth = float(np.nanmean(ent[wmask]) - bent) if wmask.sum() >= 2 else np.nan

        # --- init_floor ---
        init_floor = floor_speaker(onset_s)
        # --- init_primary: first new speaker (!= pre-window dominant) in [onset-5, onset+10] ---
        pre_dom = dom_speaker(onset_s - 15, onset_s)
        win = (onset_all >= onset_s - 5) & (onset_all <= onset_s + 10)
        idxs = np.where(win)[0]
        init_primary = None
        for i in idxs:
            if pre_dom is None or speak_all[i] != pre_dom:
                init_primary = speak_all[i]; break
        if init_primary is None:
            init_primary = init_floor
        # --- init_question: first '?' utterance in window ---
        init_question = None
        for i in idxs:
            if "?" in text_all[i]:
                init_question = speak_all[i]; break

        rows.append(dict(
            mid=mid, team=team, date=date, event_onset_s=onset_s, event_class=ev_class, event_class_s9rule=ev_class_s9, depth=depth,
            init_primary=pseudo.get(init_primary), init_floor=pseudo.get(init_floor),
            init_question=pseudo.get(init_question) if init_question else None,
            facilitator=facilitator_pseudo,
            facilitator_primary=int(pseudo.get(init_primary) == facilitator_pseudo) if init_primary else np.nan,
            facilitator_floor=int(pseudo.get(init_floor) == facilitator_pseudo) if init_floor else np.nan,
            facilitator_question=(int(pseudo.get(init_question) == facilitator_pseudo) if init_question else np.nan),
        ))

D = pd.DataFrame(rows).sort_values(["team", "date", "event_onset_s"])
D["week"] = D.groupby(["team", "mid"]).ngroup()
# proper week index: rank distinct mids per team by date
wk = D[["team", "mid", "date"]].drop_duplicates().sort_values(["team", "date"])
wk["week"] = wk.groupby("team").cumcount()
D = D.drop(columns=["week"]).merge(wk[["mid", "week"]], on="mid", how="left")

os.makedirs(f"{os.path.dirname(__file__)}/../data", exist_ok=True)
OUT = f"{os.path.dirname(__file__)}/../data/events_initiators.csv"
D.to_csv(OUT, index=False)
print(f"wrote {OUT}  ({len(D)} events, {D.mid.nunique()} meetings)")
print("\nevent class distribution:\n", D.event_class.value_counts().to_string())
print("\ninitiator definitions - non-null rate:")
for c in ["init_primary", "init_floor", "init_question"]:
    print(f"  {c}: {D[c].notna().mean()*100:.1f}% non-null")
print("\nfacilitator-initiated share by definition:")
for c in ["facilitator_primary", "facilitator_floor", "facilitator_question"]:
    print(f"  {c}: {D[c].mean()*100:.1f}%  (n={D[c].notna().sum()})")
