"""T2 - Descriptives & concentration of initiation.
- Distribution of initiations per member, per team (all 3 initiator definitions); Gini coefficient.
- initiation_lift(member) = share_of_initiations / share_of_talk_time (word-count based) -- does
  anyone initiate MORE than they talk?
- Stability: split each team's meetings into first/second half by week; Spearman r of member
  initiation-rank across halves.
Talk-time share is computed directly from the transcripts (word count per pseudonymized speaker per
meeting), not a new metric -- purely descriptive denominator for the lift ratio."""
import glob, os, re
import numpy as np, pandas as pd
from scipy.stats import spearmanr

BASE = os.path.expanduser("~/lsh-work/study9_initiators")
LSH = os.path.expanduser("~/lsh-work")
D = pd.read_csv(f"{BASE}/data/events_initiators.csv")
DEFS = ["init_primary", "init_floor", "init_question"]

# --- talk-time share per (mid, pseudo speaker) ---
tt_rows = []
for mid, g in D.groupby("mid"):
    tp = f"{LSH}/data/text_startup/{mid}_transcript.csv"
    tx = pd.read_csv(tp)
    onset = pd.to_numeric(tx.onset_seconds, errors="coerce")
    ok = onset.notna()
    tx = tx[ok]; onset = onset[ok]
    order = onset.argsort()
    spk_raw = tx.speaker_id.astype(str).to_numpy()[order]
    nw = tx.text.astype(str).str.split().apply(len).to_numpy()[order]
    seen = []
    for s in spk_raw:
        if s not in seen: seen.append(s)
    pseudo = {s: f"S{i+1}" for i, s in enumerate(seen)}
    tot = nw.sum()
    for s in set(spk_raw):
        tt_rows.append(dict(mid=mid, member=pseudo[s], talk_words=int(nw[spk_raw == s].sum()),
                             talk_share=float(nw[spk_raw == s].sum() / tot)))
TT = pd.DataFrame(tt_rows)
TT.to_csv(f"{BASE}/data/talk_time_share.csv", index=False)

def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    if n == 0 or x.sum() == 0: return np.nan
    cum = np.cumsum(x)
    return (n + 1 - 2 * (cum.sum() / cum[-1])) / n

print("=" * 90, "\nPART A - Initiation distribution per member, per team (all 3 definitions)\n" + "=" * 90)
conc_rows = []
for defn in DEFS:
    print(f"\n--- {defn} ---")
    for team, g in D.groupby("team"):
        counts = g[defn].value_counts()
        gi = gini(counts.values)
        print(f"  {team}: n_events={len(g.dropna(subset=[defn]))}  counts={counts.to_dict()}  Gini={gi:.3f}")
        conc_rows.append(dict(definition=defn, team=team, gini=gi, n_events=len(g.dropna(subset=[defn]))))
pd.DataFrame(conc_rows).to_csv(f"{BASE}/data/gini_by_team_definition.csv", index=False)

print("\n" + "=" * 90, "\nPART B - Initiation lift = share_of_initiations / share_of_talk_time\n" + "=" * 90)
lift_rows = []
for defn in DEFS:
    for team, g in D.groupby("team"):
        init_counts = g[defn].value_counts()
        init_share = init_counts / init_counts.sum()
        talk_share_team = TT[TT.mid.isin(g.mid.unique())].groupby("member").talk_words.sum()
        talk_share_team = talk_share_team / talk_share_team.sum()
        for m in init_share.index:
            ts = talk_share_team.get(m, np.nan)
            lift = init_share[m] / ts if ts and ts > 0 else np.nan
            lift_rows.append(dict(definition=defn, team=team, member=m, init_share=init_share[m],
                                   talk_share=ts, lift=lift, is_facilitator=bool(g[g[defn] == m].facilitator.iloc[0] == m) if len(g[g[defn]==m]) else False))
LIFT = pd.DataFrame(lift_rows)
LIFT.to_csv(f"{BASE}/data/initiation_lift.csv", index=False)
print(LIFT[LIFT.definition == "init_primary"].round(3).sort_values(["team", "lift"], ascending=[True, False]).to_string(index=False))

print("\n" + "=" * 90, "\nPART C - Stability: member initiation-rank, weeks 0-12 vs 13+ (first vs second half)\n" + "=" * 90)
stab_rows = []
for defn in DEFS:
    for team, g in D.groupby("team"):
        half = g.week.median()
        g = g.copy(); g["half"] = np.where(g.week <= half, "H1", "H2")
        c1 = g[g.half == "H1"][defn].value_counts()
        c2 = g[g.half == "H2"][defn].value_counts()
        members = sorted(set(c1.index) | set(c2.index))
        r1 = c1.reindex(members).fillna(0); r2 = c2.reindex(members).fillna(0)
        if len(members) >= 3:
            rho, p = spearmanr(r1, r2)
        else:
            rho, p = np.nan, np.nan
        stab_rows.append(dict(definition=defn, team=team, n_members=len(members), rho=rho, p=p,
                               H1_counts=r1.to_dict(), H2_counts=r2.to_dict()))
        print(f"{defn:14s} {team}: members={members}  H1={r1.to_dict()}  H2={r2.to_dict()}  rho={rho:.2f} p={p:.3f}" if not np.isnan(rho) else f"{defn} {team}: insufficient members")
pd.DataFrame(stab_rows).to_csv(f"{BASE}/data/stability_halves.csv", index=False)
print("\nwrote talk_time_share.csv, gini_by_team_definition.csv, initiation_lift.csv, stability_halves.csv")
