"""Verified per-meeting speaker ROLE map (no names). Built by build_speaker_roles.py from the researcher's
retained name-labeled source transcripts (never published). Roles: FACILITATOR (shared external
facilitator), A1-A3 / B1-B3 (team members, fixed roster order), DEVICE (a participant on a shared
device/room feed), BOT (transcription-tool line; removed from the canonical transcripts on 2026-09-05).

Raw speaker_id is assigned per meeting by order of first appearance and is NOT a persistent identity;
any cross-meeting aggregation by person must go through this map (AUDIT_REPORT.md, causa-raiz B)."""
import os
import pandas as pd

_ROLES = pd.read_csv(f"{os.path.dirname(os.path.abspath(__file__))}/../data/speaker_roles_verified.csv")
_ROLES["raw_id"] = _ROLES.raw_id.astype(str)

def role_map(mid):
    """raw speaker_id (str) -> role label for one meeting."""
    sub = _ROLES[_ROLES.mid == mid]
    return dict(zip(sub.raw_id, sub.role))

def short(role):
    """Compact label for figures: FACILITATOR -> F, DEVICE -> Dev, A1 -> A1."""
    return {"FACILITATOR": "F", "DEVICE": "Dev"}.get(role, role)
