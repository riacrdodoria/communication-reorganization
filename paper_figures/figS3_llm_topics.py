"""Supplementary Figure S3 — Exploratory, not validated: content-only LLM topic segmentation of the 34 meetings.
One agent per meeting with identical instructions saw only row numbers and utterance text (no speakers, no times).
A: agreement of LLM topic boundaries with other divisions (+/-30 s; observed / circular-shift expectation).
B: independent cues at topic and subtopic boundaries (transition markers and long pauses, +/-15 s).
C: floor state at boundaries (observed / expected). D: coincidence with reorganization events, by kind of new topic."""
import os, re, numpy as np, pandas as pd, matplotlib.pyplot as plt
import paper_style as ps
ps.setup(); R = os.path.expanduser("~/lsh-work/study13_metric_extensions/results"); INK, MUTED, BLUE, ORANGE = ps.INK, ps.NEUTRAL, "#1f6fb4", "#d95f02"
AG = pd.read_csv(f"{R}/llm_topics_agreement.csv"); RL = pd.read_csv(f"{R}/llm_topics_relations.csv").set_index("set"); TXT = open(f"{R}/llm_topics_summary.txt").read()
def grab(pat): return [float(x) for x in re.search(pat, TXT).groups()]
cueT = grab(r"LLMT: topic-transition marker ([\d.]+) .*?long pause ([\d.]+)"); cueS = grab(r"LLMS: topic-transition marker ([\d.]+) .*?long pause ([\d.]+)")
flT = grab(r"LLMT n=\d+: F1 ([\d.]+)\s+MIX ([\d.]+)\s+F2 ([\d.]+)"); flS = grab(r"LLMS n=\d+: F1 ([\d.]+)\s+MIX ([\d.]+)\s+F2 ([\d.]+)")
fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.2)); (axA, axB), (axC, axD) = axs; fig.subplots_adjust(hspace=.7, wspace=.5)
fig.suptitle("Exploratory, not validated: content-only LLM topic segmentation", x=.01, ha="left", fontsize=8.6, color=MUTED, y=1.0)
# A
a = AG[AG.llm == "LLMT"].set_index("other"); order = [("AGENDA", "L10 agenda"), ("TILE", "lexical tiling"), ("EMB", "embeddings"), ("NETC", "semantic network"), ("NETG", "network change")]
axA.barh(range(5), [a.loc[k, "llm_to_other"] for k, _ in order], .6, color=[BLUE] + ["#9fb6d6"] * 4); axA.set_yticks(range(5)); axA.set_yticklabels([l for _, l in order], fontsize=6.2); axA.invert_yaxis()
for i, (k, _) in enumerate(order): axA.text(a.loc[k, "llm_to_other"] + .08, i, f"{a.loc[k, 'llm_to_other']:.2f}×", va="center", fontsize=5.8, color=INK)
axA.axvline(1, color=MUTED, ls=":", lw=.7); axA.set_xlabel("coincidence / expected", fontsize=6.4); axA.tick_params(axis="x", labelsize=5.8); axA.grid(axis="y", visible=False); axA.set_xlim(0, 6)
axA.set_title("A. Topics follow the agenda", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# B
x = np.arange(2)
axB.bar(x - .18, [cueT[0], cueT[1]], .34, color=BLUE, label="topic boundary"); axB.bar(x + .18, [cueS[0], cueS[1]], .34, color="#9fb6d6", label="subtopic boundary")
for xx, v in zip(list(x - .18) + list(x + .18), cueT + cueS): axB.text(xx, v + .03, f"{v:.2f}", ha="center", fontsize=5.6, color=INK)
axB.axhline(1, color=MUTED, ls=":", lw=.7); axB.set_xticks(x); axB.set_xticklabels(["transition marker\n('então', 'bom', 'próximo')", "long pause\n(estimated)"], fontsize=5.8); axB.tick_params(axis="y", labelsize=5.8)
axB.set_ylabel("observed / expected (±15 s)", fontsize=6.4); axB.legend(fontsize=5.4, frameon=False, loc="upper right"); axB.set_ylim(0, 2.3)
axB.set_title("B. Independent cues", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# C
st = [("single-speaker", INK), ("mixed", MUTED), ("collaborative", BLUE)]
for j, ((lab, c), vT, vS) in enumerate(zip(st, flT, flS)):
    axC.bar(j - .18, vT, .34, color=c); axC.bar(j + .18, vS, .34, color=c, alpha=.45)
    axC.text(j - .18, vT + .03, f"{vT:.2f}", ha="center", fontsize=5.6); axC.text(j + .18, vS + .03, f"{vS:.2f}", ha="center", fontsize=5.6)
axC.axhline(1, color=MUTED, ls=":", lw=.7); axC.set_xticks(range(3)); axC.set_xticklabels([s[0] for s in st], fontsize=6.0); axC.tick_params(axis="y", labelsize=5.8)
axC.set_ylabel("share in floor state / expected", fontsize=6.4); axC.text(.02, .97, "solid = topic, light = subtopic", transform=axC.transAxes, va="top", fontsize=5.4, color=MUTED)
axC.set_title("C. Topic changes avoid the\nsingle-speaker floor", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# D
kinds = [("LLMT", "all topics"), ("LLMT_report", "report"), ("LLMT_decision", "decision"), ("LLMT_procedural", "procedural"), ("LLMT_problem", "problem"), ("LLMS", "subtopics")]
for i, (k, lab) in enumerate(kinds):
    r = RL.loc[k]; sig = r.event_p < .05
    axD.barh(i, r.event, .6, color=BLUE if sig else "white", edgecolor=BLUE); axD.text(r.event + .03, i, f"{r.event:.2f}× (n={int(r.n)})", va="center", fontsize=5.6, color=INK)
axD.axvline(1, color=MUTED, ls=":", lw=.7); axD.set_yticks(range(len(kinds))); axD.set_yticklabels([k[1] for k in kinds], fontsize=6.2); axD.invert_yaxis(); axD.set_xlim(0, 2.2)
axD.set_xlabel("boundaries within ±30 s of an event / expected", fontsize=6.2); axD.tick_params(axis="x", labelsize=5.8); axD.grid(axis="y", visible=False)
axD.set_title("D. Topic changes coincide\nwith reorganization", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/figS3_llm_topics.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok", cueT, flT)
