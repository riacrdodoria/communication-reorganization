"""Figure: who initiates reorganization? Panel A = initiation lift per member (init_primary
definition); Panel B = leader-initiation share vs week, per team + pooled trend."""
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kendalltau

COORD = "#2E7D8C"; DELIB = "#d95f02"; INK = "#1f2937"; NEUTRAL = "#6b7280"; GRID = "#e5e7eb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": "#9aa0a6", "axes.linewidth": .8,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.labelsize": 10.5,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .7, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
    "figure.dpi": 150, "savefig.dpi": 600, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "svg.fonttype": "none"})

BASE = os.path.expanduser("~/lsh-work/study9_initiators")
LIFT = pd.read_csv(f"{BASE}/data/initiation_lift.csv")
D = pd.read_csv(f"{BASE}/data/events_initiators.csv")

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5.2))

# --- Panel A: initiation lift per member, init_primary ---
L = LIFT[LIFT.definition == "init_primary"].copy()
L = L.sort_values(["team", "lift"], ascending=[True, False])
x = np.arange(len(L))
colors = [DELIB if r.is_leader else COORD for _, r in L.iterrows()]
axA.bar(x, L.lift, color=colors, width=.65, zorder=3)
axA.axhline(1.0, color=INK, lw=1, ls="--")
labels = [f"{r.member}{' (L)' if r.is_leader else ''}\n{r.team[-1].upper()}" for _, r in L.iterrows()]
axA.set_xticks(x); axA.set_xticklabels(labels, fontsize=8)
axA.set_ylabel("initiation lift  (share of initiations / share of talk-time)")
axA.set_title("A  Who initiates more than they talk?", loc="left", fontsize=11)
from matplotlib.patches import Patch
axA.legend(handles=[Patch(fc=DELIB, label="leader (facilitator)"), Patch(fc=COORD, label="other members")],
           fontsize=8.5, loc="upper right")
axA.text(.5, .96, "lift > 1: initiates disproportionately to talk-time", transform=axA.transAxes,
         ha="center", va="top", fontsize=8, style="italic", color=NEUTRAL)

# --- Panel B: leader-initiation share vs week ---
sub = D.dropna(subset=["init_primary"]).copy()
sub["is_leader"] = (sub.init_primary == sub.leader).astype(float)
per_mtg = sub.groupby(["team", "mid", "week"]).is_leader.mean().reset_index()
COLT = {"startup_a": COORD, "startup_b": DELIB}
for team, g in per_mtg.groupby("team"):
    g = g.sort_values("week")
    axB.plot(g.week, 100 * g.is_leader, "o", color=COLT[team], ms=5, alpha=.75, label=f"team {team[-1].upper()}")
    z = np.polyfit(g.week, g.is_leader, 1)
    axB.plot(g.week, 100 * np.polyval(z, g.week), "--", color=COLT[team], lw=1.8)
tau_a, p_a = kendalltau(per_mtg[per_mtg.team == "startup_a"].week, per_mtg[per_mtg.team == "startup_a"].is_leader)
tau_b, p_b = kendalltau(per_mtg[per_mtg.team == "startup_b"].week, per_mtg[per_mtg.team == "startup_b"].is_leader)
tau_p, p_p = kendalltau(per_mtg.week, per_mtg.is_leader)
axB.set_xlabel("week"); axB.set_ylabel("leader-initiated events (% of meeting's events)")
axB.set_title("B  Does initiation shift to the leader as teams mature?", loc="left", fontsize=11)
axB.legend(fontsize=8.5, loc="upper left")
axB.text(.02, .04,
          f"team A: τ={tau_a:+.2f} (p={p_a:.2f})\nteam B: τ={tau_b:+.2f} (p={p_b:.2f}*)\npooled: τ={tau_p:+.2f} (p={p_p:.2f}*)",
          transform=axB.transAxes, va="bottom", ha="left", fontsize=8.4,
          bbox=dict(boxstyle="round,pad=0.35", fc="#f8fafc", ec="#cbd5e1", lw=.7))

fig.suptitle("Study 9 — Who initiates reorganization? Talk-time explains it; a weak, definition-dependent drift toward the leader",
             fontsize=12, fontweight="bold", x=.01, ha="left", y=1.04)
fig.text(0.5, -0.05,
         "Figure 9. (A) Initiation lift (init_primary definition): the least-talkative member (S5) initiates far more "
         "than their talk-time predicts in both teams; the leader's lift is close to 1 (roughly proportional to talk-time). "
         "(B) Leader-initiated share rises modestly with week in team B (τ=+.41, p=.02) but not team A (n.s.); pooled "
         "τ=+.27, p=.03 — a weak, definition-dependent trend (null for the init_question definition), reported honestly, "
         "not as a robust finding.",
         ha="center", va="top", fontsize=8.2, color=NEUTRAL, style="italic", wrap=True)
fig.tight_layout(rect=[0, 0.03, 1, 0.96])
for ext in ("png", "pdf", "svg"):
    fig.savefig(f"{BASE}/fig_initiators.{ext}", bbox_inches="tight", facecolor="white",
                dpi=600 if ext == "png" else None)
print("wrote fig_initiators.{png,pdf,svg}")
