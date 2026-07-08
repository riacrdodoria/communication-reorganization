"""Composite Figure 3 — Temporal structure (Study 3 grouping here = Studies 6/7, extended by S10;
tests P4, P5). Story: within meetings, reorganization is organized by phase transitions and self-
regulates; across weeks, teams consolidate their baseline while the peaks stay invariant.
Panels A and B reuse Study 6's boundary-perturbation and review-vs-IDS logic directly.
Panel C reuses Study 7's baseline-vs-excursion developmental panel directly.
Panel D is a new panel built from Study 10's meso data (first-half vs second-half event rate;
no such panel exists in fig_early_warning.py, which only has the pre-event/ROC panels).
No source figure script is modified."""
import os
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon, kendalltau, spearmanr
import paper_style as ps
ps.setup()

L = os.path.expanduser("~/lsh-work")
GM = f"{L}/data/metrics_gorman_l8"
S10 = f"{L}/study10_early_warning/data"

# ============================================================ Panel A data (Study 6 logic)
import glob
EP = pd.read_csv(f"{L}/episode_codes.csv")
rowsA = []
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    g = pd.read_csv(f); sec = g.second.to_numpy(float); ent = g.entropy_g.to_numpy(float); det = g.det_g.to_numpy(float)
    bnds = [b for b in sorted(EP[EP.mid == mid].sec_start.tolist()) if b > sec.min() + 30]
    if not bnds: continue
    near = np.zeros(len(sec), bool)
    for b in bnds: near |= (np.abs(sec - b) <= 30)
    if near.sum() < 5 or (~near).sum() < 5: continue
    rowsA.append(dict(e_b=np.nanmean(ent[near]), e_i=np.nanmean(ent[~near]), d_b=np.nanmean(det[near]), d_i=np.nanmean(det[~near])))
BA = pd.DataFrame(rowsA)
peA = wilcoxon(BA.e_b, BA.e_i).pvalue; pdA = wilcoxon(BA.d_b, BA.d_i).pvalue
deA = BA.e_b.mean() - BA.e_i.mean(); ddA = BA.d_b.mean() - BA.d_i.mean()

# ============================================================ Panel B data (Study 6 logic)
P = pd.read_csv(f"{L}/l10_stage_metrics.csv")
REV = ["scorecard", "rock_review", "todo"]
recB = []
for mid, g in P.groupby("mid"):
    rv = g[g.stage.isin(REV)]; iv = g[g.stage == "ids"]
    if len(rv) and len(iv):
        recB.append((np.average(rv.entropy, weights=rv.secs), iv.entropy.mean(),
                     np.average(rv.reorg_rate, weights=rv.secs), iv.reorg_rate.mean()))
RB = pd.DataFrame(recB, columns=["rev_e", "ids_e", "rev_r", "ids_r"])
pe2 = wilcoxon(RB.rev_e, RB.ids_e).pvalue; pr2 = wilcoxon(RB.rev_r, RB.ids_r).pvalue

# ============================================================ Panel C data (Study 7 logic)
dep = pd.read_csv(f"{L}/reorg_depth_longitudinal_panel.csv")
tb, pb = kendalltau(dep.week, dep.base_ent)
te, pe = kendalltau(dep.dropna(subset=["BORDER_ent_exc"]).week, dep.dropna(subset=["BORDER_ent_exc"]).BORDER_ent_exc)

# ============================================================ Panel D data (new, from Study 10)
meso = pd.read_csv(f"{S10}/meso_halves.csv")
rho, prho = spearmanr(meso.h1_event_rate, meso.h2_event_rate)

# ============================================================ Layout: 2x2, ~7.0 x 5.5 in
fig = plt.figure(figsize=(7.0, 5.5))
gs = fig.add_gridspec(2, 2, hspace=.62, wspace=.38)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1])
axC = fig.add_subplot(gs[1, 0]); axD = fig.add_subplot(gs[1, 1])

# --- A: boundary perturbation ---
x = np.arange(2); w = .32
axA.bar(x - w / 2, [BA.e_b.mean(), BA.d_b.mean()], w, color=ps.DELIB, label="±30s of boundary", zorder=3)
axA.bar(x + w / 2, [BA.e_i.mean(), BA.d_i.mean()], w, color=ps.COORD, label="episode interior", zorder=3)
axA.set_xticks(x); axA.set_xticklabels(["entropy\n(↑ reorg.)", "%DET\n(↓ reorg.)"], fontsize=7)
axA.set_ylabel("metric value", fontsize=7.4); axA.set_ylim(0, 95)
axA.legend(loc="upper center", fontsize=5.8, frameon=False)
axA.set_title("A. Boundaries as\nperturbations", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axA.text(.98, .04, f"Δent={deA:+.1f} {ps.stars(peA)}\nΔ%DET={ddA:+.1f} {ps.stars(pdA)}", transform=axA.transAxes,
          fontsize=5.8, va="bottom", ha="right", bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

# --- B: procedural review > IDS ---
x2 = np.arange(2)
axB.bar(x2 - w / 2, [RB.rev_e.mean(), RB.rev_r.mean()], w, color=ps.COORD, label="procedural review", zorder=3)
axB.bar(x2 + w / 2, [RB.ids_e.mean(), RB.ids_r.mean()], w, color=ps.DELIB, label="IDS (problem-solving)", zorder=3)
axB.set_xticks(x2); axB.set_xticklabels(["entropy", "reorg-rate (%)"], fontsize=7)
axB.set_ylabel("value", fontsize=7.4); axB.set_ylim(0, 45)
axB.legend(loc="upper right", fontsize=5.6, frameon=False)
axB.set_title("B. Procedural review\n> problem-solving", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axB.text(.98, .70, f"Δent={RB.rev_e.mean()-RB.ids_e.mean():+.1f} {ps.stars(pe2)}\nΔrate={RB.rev_r.mean()-RB.ids_r.mean():+.1f} {ps.stars(pr2)}",
          transform=axB.transAxes, fontsize=5.8, va="top", ha="right", bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

# --- C: developmental baseline vs excursion ---
for team, g in dep.groupby("team"):
    g = g.sort_values("week")
    axC.plot(g.week, g.base_ent, "o-", color=ps.TEAM[team], ms=2.4, lw=.7, alpha=.4)
    axC.plot(g.week, g.base_ent + g.BORDER_ent_exc, "^--", color=ps.TEAM[team], ms=2.4, lw=.7, alpha=.85)
    zb = np.polyfit(g.week, g.base_ent, 1); axC.plot(g.week, np.polyval(zb, g.week), "-", color=ps.TEAM[team], lw=1.8)
axC.plot([], [], "o-", color=ps.INK, label="baseline (resting)")
axC.plot([], [], "^--", color=ps.INK, label="at border events")
axC.set_xlabel("week", fontsize=7.4); axC.set_ylabel("team-state entropy", fontsize=7.4)
axC.set_title("C. Consolidation\n(baseline ↓, excursion stable)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axC.legend(loc="upper right", fontsize=5.6, frameon=False)
axC.text(.02, .04, f"baseline τ={tb:+.2f} {ps.stars(pb)}\nexcursion τ={te:+.2f} {ps.stars(pe)}", transform=axC.transAxes,
          fontsize=5.8, va="bottom", ha="left", bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

# --- D: within-meeting reorganization budget (new, S10 data) ---
TEAMMARK = {"startup_a": "o", "startup_b": "s"}
for team, g in meso.groupby("team"):
    axD.scatter(g.h1_event_rate, g.h2_event_rate, color=ps.TEAM[team], marker=TEAMMARK[team], s=22,
                 alpha=.85, edgecolor="white", lw=.4, zorder=3, label={"startup_a": "Team A", "startup_b": "Team B"}[team])
zz = np.polyfit(meso.h1_event_rate, meso.h2_event_rate, 1)
xx = np.linspace(meso.h1_event_rate.min(), meso.h1_event_rate.max(), 50)
axD.plot(xx, np.polyval(zz, xx), "-", color=ps.INK, lw=1.4, zorder=2)
axD.set_xlabel("first-half event rate (%)", fontsize=7.2); axD.set_ylabel("second-half event rate (%)", fontsize=7.2)
axD.set_title("D. Within-meeting budget\n(not momentum, S10)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axD.legend(loc="upper right", fontsize=5.8, frameon=False)
axD.text(.98, .04, f"ρ={rho:+.2f}, p={prho:.1e}\n(both teams)", transform=axD.transAxes, fontsize=5.8, va="bottom",
          ha="right", bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

fig.suptitle("Figure 3 — Temporal structure of communication reorganization", fontsize=10.5,
             fontweight="bold", x=.01, ha="left", y=1.015)
ps.caption(fig, "Figure 3. Temporal structure (Studies 6, 7; extended by S10). (A) Mean entropy and "
    "%DET in ±30s windows centered on topic-episode boundaries vs matched interior windows (paired "
    "Wilcoxon, non-circular: boundaries from content, metrics from turn-taking). (B) Reorganization rate "
    "and entropy by EOS Level 10 protocol stage; procedural review (teal) reorganizes significantly more "
    "than problem-solving (IDS; orange). (C) Per-meeting baseline entropy and above-baseline excursion "
    "over ~26 weeks (Kendall tau); baseline entropy declines (consolidation) while excursion depth is "
    "flat - a stereotyped event riding a sinking baseline; both teams shown, replicating in direction "
    "(S11). (D) First-half meeting reorganization rate vs second-half rate (Spearman rho); both teams "
    "show a negative relationship, indicating a within-meeting reorganization budget rather than "
    "momentum (S10).", y=-0.1, fontsize=6.2)
fig.tight_layout(rect=[0, 0.08, 1, 0.95])
for ext in ("png", "pdf"):
    fig.savefig(f"{os.path.dirname(__file__)}/fig3_temporal_structure.{ext}", bbox_inches="tight",
                facecolor="white", dpi=600 if ext == "png" else None)
print("wrote fig3_temporal_structure.{png,pdf}")
print(f"rho={rho:.3f} p={prho:.2e}  tb={tb:.3f} te={te:.3f}")
