"""Composite Figure 2 — Individual and team-level structure (Study 2; tests P2, P3; corroborated
by S9, S12). Story: reorganization is coordination, not deliberation, at the content level, the
floor level, and the affective level, and it opens from the quietest members up.
Panel A reuses Study 3's 40-category content-fingerprint lift (compact form: only 6 illustrative
categories labeled, per storyboard spec; all 40 drawn as lollipops, non-significant grayed).
Panel B is a new panel: all 9 floor/centrality measures (Study 4 logic + gini_turns, which the
original single-study figure omits for space).
Panel C is a new panel: initiation lift aggregated to 3 ROLE categories (facilitator / most-
talkative member / quietest member) rather than Study 9's per-individual-member view.
Panel D reuses Study 12's 8-category socioemotional lift, compacted, with a small timing inset.
No source figure script is modified."""
import os
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, wilcoxon
import paper_style as ps
ps.setup()

L = os.path.expanduser("~/lsh-work")
S9 = f"{L}/study9_initiators/data"
S12 = f"{L}/study12_socioemotional/data"

# ============================================================ Panel A data (Study 3 logic)
df = pd.read_csv(f"{L}/peaks_taxonomy_sig.csv")
dA = df[(df.metric == "rmse_g") & (df.side == "peak")].copy()
TAX = {**{c: "CACS" for c in ['arguable', 'converge', 'disagree', 'delim', 'nonarg']},
       **{c: "IAM" for c in ['iam1', 'iam2', 'iam3', 'iam4', 'iam5']}, **{c: "Mercer" for c in ['disput', 'cumul', 'explor']},
       **{c: "Bales" for c in ['bgiveinfo', 'bgiveopin', 'bgivesug', 'baskinfo', 'baskopin', 'basksug', 'bsolid', 'btension', 'bagree', 'bdisagree', 'btensh', 'bantag']},
       **{c: "act4teams" for c in ['namep', 'linkp', 'names', 'links', 'linkc', 'cprod', 'proact', 'struct', 'ginfo', 'ktrans', 'coop']},
       **{c: "ISO" for c in ['qset', 'qprop', 'directive', 'commissive', 'feedback']}}
dA = dA[dA.cat.isin(TAX)].copy(); dA = dA.sort_values("mean_lift")
HIGHLIGHT = {"struct": "structuring", "baskinfo": "asks-info", "bagree": "agree",
             "arguable": "arguable", "bgiveopin": "gives-opinion", "iam3": "negotiation"}

# ============================================================ Panel B data (Study 4 logic + gini_turns)
F = pd.read_csv(f"{L}/floor_windows.csv")
MEAS = [("top_share", "Top-speaker share", "concentration"), ("net_central", "Network centralization", "concentration"),
        ("eig_central", "Eigenvector centrality", "concentration"), ("gini_words", "Participation Gini (words)", "concentration"),
        ("gini_turns", "Participation Gini (turns)", "concentration"), ("inout_asym", "In-out influence asymmetry", "concentration"),
        ("turnlen_disp", "Turn-length dispersion", "concentration"), ("n_active", "Active speakers/window", "breadth"),
        ("part_entropy", "Participation entropy*", "breadth")]
rowsB = []
for col, name, fam in MEAS:
    rs = []
    for mid, g in F.groupby("mid"):
        gg = g.dropna(subset=[col, "det_g"])
        if len(gg) < 8 or gg[col].std() == 0: continue
        rs.append(pearsonr(gg[col], gg.det_g)[0])
    rs = [r for r in rs if np.isfinite(r)]
    rowsB.append(dict(name=name, fam=fam, r=np.mean(rs), n=len(rs), p=wilcoxon(rs).pvalue))
dB = pd.DataFrame(rowsB).sort_values("r")

# ============================================================ Panel C data (aggregated to 3 roles)
LIFT = pd.read_csv(f"{S9}/initiation_lift.csv"); LIFT = LIFT[LIFT.definition == "init_primary"]
PERM = pd.read_csv(f"{S9}/permutation_facilitator_share.csv")
roleC = {"facilitator": [], "most-talkative\nmember": [], "quietest\nmember": []}
for team, g in LIFT.groupby("team"):
    fac = g[g.is_facilitator]; roleC["facilitator"].append((team, fac.lift.iloc[0]))
    others = g[~g.is_facilitator]
    dom = others.loc[others.talk_share.idxmax()]; roleC["most-talkative\nmember"].append((team, dom.lift))
    quiet = others.loc[others.talk_share.idxmin()]; roleC["quietest\nmember"].append((team, quiet.lift))

# ============================================================ Panel D data (Study 12 logic)
dD = pd.read_csv(f"{S12}/socioemotional_lifts.csv").sort_values("mean_lift")
timing = pd.read_csv(f"{S12}/socioemotional_timing.csv")

# ============================================================ Layout: 2x2, ~7.0 x 5.5 in
fig = plt.figure(figsize=(7.0, 5.5))
gs = fig.add_gridspec(2, 2, hspace=.62, wspace=.42)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1])
axC = fig.add_subplot(gs[1, 0]); axD = fig.add_subplot(gs[1, 1])

# --- A: content fingerprint (compact) ---
# clip the nonarg outlier (+0.80) view range slightly wider so it isn't fully truncated
y = np.arange(len(dA))
sig = dA.q_fdr < .05
col = [(ps.COORD if v > 0 else ps.DELIB) for v in dA.mean_lift]
alpha = [1.0 if s else .28 for s in sig]
for yi, ci, ai, li in zip(y, col, alpha, dA.mean_lift):
    axA.hlines(yi, 0, li, color=ci, lw=1.5, alpha=ai, zorder=2)
axA.scatter(dA.mean_lift, y, color=col, s=7, alpha=alpha, zorder=3, lw=0)
axA.axvline(0, color=ps.INK, lw=.7); axA.set_yticks([]); axA.set_xlim(-.42, .85)
axA.set_xlabel("density lift at events", fontsize=7.2)
axA.set_title("A. Content fingerprint\n(6 schemes, 40 categories)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
# side legend of illustrative categories (NOT inline labels - rows are too dense at this panel
# size for per-bar text; a small side list avoids overlap while still naming examples)
mid_y = len(dA) / 2
ex_txt = ("COORDINATION (rises)\n" + "\n".join(f"  {v} (+{dA.set_index('cat').loc[k,'mean_lift']:.2f})"
          for k, v in HIGHLIGHT.items() if dA.set_index('cat').loc[k, 'mean_lift'] > 0) +
          "\n\nDELIBERATION (falls)\n" + "\n".join(f"  {v} ({dA.set_index('cat').loc[k,'mean_lift']:.2f})"
          for k, v in HIGHLIGHT.items() if dA.set_index('cat').loc[k, 'mean_lift'] < 0))
axA.text(.20, mid_y, ex_txt, fontsize=5.6, va="center", ha="left", color=ps.INK, linespacing=1.5,
          bbox=dict(boxstyle="round,pad=0.35", fc="#f8fafc", ec="#cbd5e1", lw=.5))
axA.text(.98, .03, "28/40 sig.; 37/40 same\ndir. across teams\n(S11: r=.969)", transform=axA.transAxes,
          fontsize=5.8, va="bottom", ha="right", bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

# --- B: floor structure (9 measures) ---
yb = np.arange(len(dB))
colb = [ps.COORD if f == "concentration" else ps.DELIB for f in dB.fam]
axB.hlines(yb, 0, dB.r, color=colb, lw=2, zorder=2)
axB.scatter(dB.r, yb, color=colb, s=24, zorder=3, edgecolor="white", lw=.5)
for yi, (_, r) in zip(yb, dB.iterrows()):
    off = .02 if r.r >= 0 else -.02; ha = "left" if r.r >= 0 else "right"
    axB.text(r.r + off, yi, f"{r['name']}", va="center", ha=ha, fontsize=5.6, color=ps.INK)
axB.axvline(0, color=ps.INK, lw=.7); axB.set_yticks([]); axB.set_xlim(-.85, .95)
axB.set_xlabel("within-meeting r with %DET", fontsize=7.2)
axB.set_title("B. Floor structure\n(F1 → F2)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axB.text(.98, .03, "9/9 same direction\ntop-share r=+.52", transform=axB.transAxes, fontsize=5.8, va="bottom",
          ha="right", bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

# --- C: who opens the floor (3 role categories) ---
xcats = list(roleC.keys())
TEAMCOL = {"startup_a": ps.COORD, "startup_b": ps.DELIB}
TEAMMARK = {"startup_a": "o", "startup_b": "s"}  # shape, not just color/hue - grayscale-legible
for xi, cat in enumerate(xcats):
    for team, val in roleC[cat]:
        axC.scatter(xi + (-.08 if team == "startup_a" else .08), val, color=TEAMCOL[team],
                     marker=TEAMMARK[team], s=36, zorder=3, edgecolor="white", lw=.5)
axC.axhline(1.0, color=ps.INK, lw=1, ls="--")
axC.set_xticks(range(len(xcats))); axC.set_xticklabels(xcats, fontsize=6.6)
axC.set_ylabel("initiation lift\n(init. share / talk-time share)", fontsize=6.8)
axC.set_title("C. Who opens the floor\n(S9)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
from matplotlib.lines import Line2D
axC.legend(handles=[Line2D([], [], marker="o", ls="", color=ps.COORD, label="Team A"),
                     Line2D([], [], marker="s", ls="", color=ps.DELIB, label="Team B")],
           fontsize=5.8, loc="upper left", frameon=False)
axC.text(.98, .97, "facilitator initiates less\nthan talk-time predicts\n(perm. p<.01, all 3 defs.)\n"
                    "quiet member lift 1.4-1.9×", transform=axC.transAxes, fontsize=5.8, va="top", ha="right",
          bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#cbd5e1", lw=.5))

# --- D: affective signature (8 categories + timing inset) ---
yd = np.arange(len(dD))
cold = [ps.COORD if v == "+" else ps.DELIB for v in dD.valence]
axD.hlines(yd, 0, dD.mean_lift, color=cold, lw=2, zorder=2)
axD.scatter(dD.mean_lift, yd, color=cold, s=24, zorder=3, edgecolor="white", lw=.5)
LABD = {"bagree": "agree", "pos": "pos (act4teams)", "bsolid": "solidarity", "btensh": "tension",
        "btension": "tension release", "bdisagree": "disagree", "neg": "neg (act4teams)"}
for yi, (_, r) in zip(yd, dD.iterrows()):
    off = .012 if r.mean_lift >= 0 else -.012; ha = "left" if r.mean_lift >= 0 else "right"
    star = "***" if r.q_fdr < .001 else "n.s."
    axD.text(r.mean_lift + off, yi, f"{LABD.get(r['cat'], r['cat'])} {star}", va="center", ha=ha, fontsize=5.4, color=ps.INK)
axD.axvline(0, color=ps.INK, lw=.7); axD.set_yticks([]); axD.set_xlim(-.08, .60)
axD.set_xlabel("density lift at events", fontsize=7.2)
axD.set_title("D. Affective signature\n(S12)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axIns = axD.inset_axes([0.66, 0.40, 0.30, 0.34])
for label, color, ls, mk in [("positive composite", ps.COORD, "-", "o"), ("negative composite", ps.DELIB, "--", "s")]:
    r = timing[timing.label == label].iloc[0]
    axIns.plot([0, 1, 2], [r.pre, r["at"], r.post], ls, marker=mk, color=color, lw=1.2, markersize=2.6)
axIns.set_xticks([0, 1, 2]); axIns.set_xticklabels(["pre", "at", "post"], fontsize=4.6)
axIns.set_yticks([]); axIns.set_title("timing (90s grain)", fontsize=5.2, pad=1.5)
fig.text(.985, .06, "pos>neg: 27/34 mtgs\n(p=1.06e-4); peak\ncoincident, not prior", fontsize=5.6, ha="right", va="bottom",
         transform=axD.transAxes, bbox=dict(boxstyle="round,pad=0.22", fc="#f8fafc", ec="#cbd5e1", lw=.5))

fig.suptitle("Figure 2 — Individual and team-level structure of communication reorganization", fontsize=10.5,
             fontweight="bold", x=.01, ha="left", y=1.015)
ps.caption(fig, "Figure 2. Individual and team-level structure (Study 2, with S9 and S12 corroborations). "
    "(A) Per-category event-vs-baseline density lift across six coding schemes (40 categories, BH-FDR); "
    "teal=coordination-type (rises), orange=deliberation-type (falls), faint=non-significant. Cross-team "
    "profile replication r=.969 (S11). (B) Nine coding-free floor/centralization measures at events vs "
    "baseline; all nine move in the same direction (floor equalizes, decentralizes), consistent with "
    "Edelsky's (1981) F1-to-F2 transition. (C) Initiation lift by speaker role; the external facilitator "
    "initiates significantly less than their talk-time predicts (permutation p<.01, all three initiator "
    "definitions); the quietest member initiates 1.4-1.9x their talk-time share (S9). (D) "
    "Event-vs-baseline lift for eight affect codes (Bales IPA + act4teams pos/neg); agreement, positive "
    "affect, and solidarity rise significantly (q<.001); no negative code survives FDR; the positive "
    "signal peaks coincident with event onset (inset), not before or after (S12).", y=-0.1, fontsize=6.2)
fig.tight_layout(rect=[0, 0.08, 1, 0.95])
for ext in ("png", "pdf"):
    fig.savefig(f"{os.path.dirname(__file__)}/fig2_multilevel_structure.{ext}", bbox_inches="tight",
                facecolor="white", dpi=600 if ext == "png" else None)
print("wrote fig2_multilevel_structure.{png,pdf}")
