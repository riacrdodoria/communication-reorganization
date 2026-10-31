"""Figure 3 — Reorganization, the agenda and the floor (Paper 1, Study 3).
A: reorganization event rate around agenda-stage onsets (15-s bins; relative to the meeting event rate), real events vs
   surrogate events (same detection rule on run-shuffled series; 95 % band).
B: floor state at agenda-stage onsets and at entropy level shifts (observed / circular-shift expectation).
C: events per 5-min block by within-meeting centralization of the turn network (quintiles; mean +/- SE), per team.
D: the agenda effects in each team (observed / surrogate events; filled = beyond all 20 surrogate sets)."""
import os, sys, json, numpy as np, pandas as pd, matplotlib.pyplot as plt
import paper_style as ps
ps.setup(); L = os.path.expanduser("~/lsh-work"); R = f"{L}/study13_metric_extensions/results"; sys.path.insert(0, f"{L}/study13_metric_extensions/src"); import common as CM
BLUE, ORANGE, INK, MUTED = "#1f6fb4", "#d95f02", ps.INK, ps.NEUTRAL; TEAM = {"A": BLUE, "B": ORANGE}
P = json.load(open(f"{R}/partitions_bounds.json")); SUR = json.load(open(f"{R}/surrogate_events.json")); EV = CM.events()
fig = plt.figure(figsize=(7.2, 5.4)); gs = fig.add_gridspec(2, 2, hspace=.62, wspace=.42)
axA, axB, axC, axD = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
# A
BINS = np.arange(-120, 121, 15)
def curve(evsets):
    num = np.zeros(BINS.size - 1); den = np.zeros(BINS.size - 1)
    for m in CM.meetings():
        ev = np.asarray(evsets[m], float); ag = np.array(P[m]["agenda"]); T = P[m]["T"]
        if ag.size == 0 or ev.size == 0: continue
        rate = ev.size / T
        for a in ag: num += np.histogram(ev - a, BINS)[0]; den += rate * 15 * np.array([(a + x) >= 0 and (a + y) <= T for x, y in zip(BINS[:-1], BINS[1:])])
    return num / np.maximum(den, 1e-9)
o = curve({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in CM.meetings()}); s = np.array([curve({m: SUR[m][k] for m in CM.meetings()}) for k in range(20)])
lo, hi = np.percentile(s, [2.5, 97.5], 0); x = BINS[:-1] + 7.5
axA.fill_between(x, lo, hi, step="mid", color="#d9dee4", label="surrogate events, 95 %")
axA.bar(x, o, width=12, color=[BLUE if v > h else "#9fb6d6" for v, h in zip(o, hi)], zorder=3, label="real events")
axA.axhline(1, color=MUTED, ls=":", lw=.7); axA.axvline(0, color=INK, lw=.7, ls="--"); axA.set_xticks([-120, -60, 0, 60, 120]); axA.tick_params(labelsize=5.8)
axA.set_xlabel("seconds from the start of an agenda stage", fontsize=6.4); axA.set_ylabel("event rate / meeting rate", fontsize=6.4); axA.legend(fontsize=5.4, frameon=False, loc="upper right")
axA.set_title("A. Reorganization closes an agenda item", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# B
SB = pd.read_csv(f"{R}/floor_cycle_T2_boundaries.csv").set_index("boundary")
rows = [("agenda", "agenda stage onset"), ("level", "entropy level shift")]; states = [("F1", "single-speaker", INK), ("MIX", "mixed", MUTED), ("F2", "collaborative", BLUE)]
for i, (k, lab) in enumerate(rows):
    for j, (st, sl, c) in enumerate(states):
        v = SB.loc[k, f"{st}_ratio"]; sig = SB.loc[k, f"{st}_p_enrich"] < .01 or SB.loc[k, f"{st}_p_deplete"] < .01
        axB.bar(i * 4 + j, v, .8, color=c if sig else "white", edgecolor=c, lw=1, label=sl if i == 0 else None)
        axB.text(i * 4 + j, v + .04, f"{v:.2f}", ha="center", fontsize=5.4, color=INK)
axB.axhline(1, color=MUTED, ls=":", lw=.7); axB.set_xticks([1, 5]); axB.set_xticklabels([r[1] for r in rows], fontsize=6.2); axB.tick_params(axis="y", labelsize=5.8)
axB.set_ylabel("share in floor state / expected", fontsize=6.4); axB.set_ylim(0, 1.8); axB.legend(fontsize=5.4, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.16), ncol=3, title="floor state (filled: p < .01)", title_fontsize=5.4)
axB.set_title("B. Agenda transitions happen with the floor open", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# C
B4 = pd.read_csv(f"{R}/floor_cycle_T4_blocks.csv"); B4["team"] = B4.mid.map(CM.team)
B4["ev"] = [int(np.sum((EV[EV.mid == m].event_onset_s >= s0) & (EV[EV.mid == m].event_onset_s < s0 + 300))) for m, s0 in zip(B4.mid, B4.s0)]
B4["cz"] = B4.groupby("mid").central.transform(lambda v: (v - v.mean()) / v.std()); B4 = B4.dropna(subset=["cz"]); B4["q"] = pd.qcut(B4.cz, 5, labels=False)
RP = pd.read_csv(f"{R}/replication_by_team.csv").set_index("headline")
for t, g in B4.groupby("team"):
    m_ = g.groupby("q").ev.mean(); se = g.groupby("q").ev.sem(); axC.errorbar(m_.index + (-.08 if t == "A" else .08), m_, yerr=se, fmt="-o", ms=3, lw=1, color=TEAM[t], capsize=2, label=f"Team {t}")
rr = RP.loc["Centralized stretches have fewer events"]
axC.text(.97, .97, f"rate ratio per SD: A {rr.A:.2f}, B {rr.B:.2f}", transform=axC.transAxes, ha="right", va="top", fontsize=5.6, color=INK)
axC.set_xticks(range(5)); axC.set_xticklabels(["least", "", "", "", "most"], fontsize=5.8); axC.set_xlabel("centralization of the turn network (quintile within meeting)", fontsize=6.2)
axC.set_ylabel("events per 5 min", fontsize=6.4); axC.tick_params(axis="y", labelsize=5.8); axC.legend(fontsize=5.4, frameon=False, loc="lower left")
axC.set_title("C. Centralized talk reorganizes less", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# D
H = [("Events anticipate the next agenda stage (15-60 s)", "event 15-60 s before\nthe next stage"), ("Events coincide with agenda transitions", "event within ±30 s\nof a stage onset")]
for i, (h, lab) in enumerate(H):
    r = RP.loc[h]
    for t, off in [("A", -.12), ("B", .12)]:
        v, p = r[t], r[f"{t}_p"]; axD.scatter(v, i + off, s=26, color=TEAM[t] if p < .05 else "white", edgecolor=TEAM[t], lw=1, zorder=3, label=f"Team {t}" if i == 0 else None)
axD.axvline(1, color=MUTED, ls=":", lw=.7); axD.set_yticks(range(len(H))); axD.set_yticklabels([l for _, l in H], fontsize=6.0); axD.set_xlim(.8, 2); axD.set_ylim(-.6, 1.6)
axD.set_xlabel("real / surrogate events", fontsize=6.4); axD.tick_params(axis="x", labelsize=5.8); axD.legend(fontsize=5.4, frameon=False, loc="lower right"); axD.grid(axis="y", visible=False)
axD.set_title("D. In each team", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/fig3_agenda_floor.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok", np.round(o, 2))
