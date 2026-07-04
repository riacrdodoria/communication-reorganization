"""T4 - Longitudinal: does facilitator-initiation share rise with week (link to Study 5 consolidation)?
T5 - Depth by initiator type: do facilitator-initiated events differ in depth from member-initiated ones?
"""
import os
import numpy as np, pandas as pd
from scipy.stats import kendalltau, mannwhitneyu, wilcoxon

BASE = os.path.expanduser("~/lsh-work/study9_initiators")
D = pd.read_csv(f"{BASE}/data/events_initiators.csv")
DEFS = ["init_primary", "init_floor", "init_question"]

print("=" * 90, "\nT4 - Facilitator-initiation share vs week (per-meeting), Kendall tau\n" + "=" * 90)
long_rows = []
for defn in DEFS:
    sub = D.dropna(subset=[defn]).copy()
    sub["is_facilitator"] = (sub[defn] == sub.facilitator).astype(float)
    per_mtg = sub.groupby(["team", "mid", "week"]).is_facilitator.mean().reset_index()
    for team, g in per_mtg.groupby("team"):
        if len(g) >= 6:
            tau, p = kendalltau(g.week, g.is_facilitator)
        else:
            tau, p = np.nan, np.nan
        long_rows.append(dict(definition=defn, team=team, n_meetings=len(g), tau=tau, p=p))
        print(f"{defn:14s} {team}: n={len(g)}  tau={tau:+.2f}  p={p:.3f}"
              if not np.isnan(tau) else f"{defn} {team}: insufficient")
    tau, p = kendalltau(per_mtg.week, per_mtg.is_facilitator)
    long_rows.append(dict(definition=defn, team="pooled", n_meetings=len(per_mtg), tau=tau, p=p))
    print(f"{defn:14s} pooled  : n={len(per_mtg)}  tau={tau:+.2f}  p={p:.3f}")
LONG = pd.DataFrame(long_rows)
LONG.to_csv(f"{BASE}/data/facilitator_share_vs_week.csv", index=False)

print("\n" + "=" * 90, "\nT5 - Event depth by initiator type (facilitator vs member)\n" + "=" * 90)
depth_rows = []
for defn in DEFS:
    sub = D.dropna(subset=[defn, "depth"]).copy()
    sub["init_type"] = np.where(sub[defn] == sub.facilitator, "facilitator", "member")
    # (a) pooled Mann-Whitney, event as unit, per team
    for team, g in sub.groupby("team"):
        a = g[g.init_type == "facilitator"].depth; b = g[g.init_type == "member"].depth
        if len(a) >= 5 and len(b) >= 5:
            U, p = mannwhitneyu(a, b)
        else:
            U, p = np.nan, np.nan
        depth_rows.append(dict(definition=defn, team=team, level="event", n_facilitator=len(a), n_member=len(b),
                                mean_facilitator=a.mean(), mean_member=b.mean(), test="Mann-Whitney U", stat=U, p=p))
        print(f"{defn:14s} {team} (event-level): facilitator depth={a.mean():.2f} (n={len(a)}) vs "
              f"member depth={b.mean():.2f} (n={len(b)})  MWU p={p:.3f}" if not np.isnan(p) else "insufficient")
    # (b) meeting as unit: mean depth per initiator-type per meeting, paired Wilcoxon
    per_mtg = sub.groupby(["mid", "init_type"]).depth.mean().unstack()
    per_mtg = per_mtg.dropna()
    if len(per_mtg) >= 8:
        stat, p = wilcoxon(per_mtg["facilitator"], per_mtg["member"])
    else:
        stat, p = np.nan, np.nan
    depth_rows.append(dict(definition=defn, team="pooled", level="meeting", n_facilitator=len(per_mtg), n_member=len(per_mtg),
                            mean_facilitator=per_mtg["facilitator"].mean() if len(per_mtg) else np.nan,
                            mean_member=per_mtg["member"].mean() if len(per_mtg) else np.nan,
                            test="paired Wilcoxon", stat=stat, p=p))
    print(f"{defn:14s} pooled (meeting-level, n={len(per_mtg)}): facilitator mean depth={per_mtg['facilitator'].mean():.2f} "
          f"vs member={per_mtg['member'].mean():.2f}  paired Wilcoxon p={p:.3f}" if len(per_mtg) else "insufficient")
DEPTH = pd.DataFrame(depth_rows)
DEPTH.to_csv(f"{BASE}/data/depth_by_initiator_type.csv", index=False)
print("\nwrote facilitator_share_vs_week.csv, depth_by_initiator_type.csv")
