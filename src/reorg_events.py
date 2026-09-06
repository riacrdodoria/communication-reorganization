"""Shared event clustering + trigger classification (2026-09-05; AUDIT_REPORT.md S7 #3/#4).

Before this module Study 7 (reorg_signature.py) and Study 9 (build_events_initiators.py) each had their own
copy of the handoff rule and they disagreed (anchor = cluster centre vs onset; window = ±30 vs ±15 s;
dominance weight = turns vs words): 279/162 vs 190/251 INTERIOR_HANDOFF/OTHER, 57% agreement on interior
events. The CANONICAL rule is Study 7's (centre, ±30 s, turn-count dominance); the alternatives are
exposed as parameters so the sensitivity can be reported (reorg_class_sensitivity.py).
"""
import numpy as np

GAP_S = 8          # consecutive event-seconds closer than this belong to the same event
TRANS_S = 30       # |centre - boundary| <= TRANS_S  -> TRANSITION

def cluster_events(evsec, gap=GAP_S):
    """Cluster sorted event-seconds into events; returns list of lists of seconds."""
    ev, cur = [], []
    for s in evsec:
        if cur and s - cur[-1] > gap:
            ev.append(cur); cur = []
        cur.append(s)
    if cur: ev.append(cur)
    return ev

def dominant(onset, spk, weight, a, b):
    """Dominant speaker in [a, b) by summed weight (turns or words). None if nobody spoke."""
    m = (onset >= a) & (onset < b)
    if not m.any(): return None
    s = {}
    for sp, w in zip(spk[m], weight[m]): s[sp] = s.get(sp, 0) + w
    return max(s, key=s.get)

def classify(ev, boundaries, onset, spk, nw, anchor="center", window=30, weight="turns", trans_s=TRANS_S):
    """Trigger class of one clustered event.
    anchor: 'center' (Study 7, canonical) or 'onset' (old Study 9)
    window: half-width in s of the before/after dominance windows (30 canonical; 15 old Study 9)
    weight: 'turns' (canonical) or 'words'
    Returns (cls, center, onset_s) with cls in {TRANSITION, INTERIOR_HANDOFF, INTERIOR_OTHER}."""
    center = float(np.mean(ev)); onset_s = float(ev[0])
    if any(abs(center - b) <= trans_s for b in boundaries):
        return "TRANSITION", center, onset_s
    t = center if anchor == "center" else onset_s
    w = np.ones_like(nw) if weight == "turns" else nw
    db = dominant(onset, spk, w, t - window, t); da = dominant(onset, spk, w, t, t + window)
    return ("INTERIOR_HANDOFF" if (db is not None and da is not None and db != da) else "INTERIOR_OTHER"), center, onset_s
