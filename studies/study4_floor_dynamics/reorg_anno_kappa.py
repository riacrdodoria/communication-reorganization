"""Reliability of the interior-reorganization interactional typology. Two independent annotators labelled
the same blind windows into a 6-type codebook (HANDOFF, CO_CONSTRUCTION, QA_CLARIFICATION,
DECISION_CONVERGENCE, ENTRY_EXIT, OTHER). Computes Cohen's kappa (A vs B), the consensus distribution, and
the coarse agreement with the rule-based mechanism. Reads label files only (no transcript text):
reorg_anno_A.json, reorg_anno_B.json (id->label), reorg_anno_hidden.json (id->{mid,c,rule_primary}).
The source windows themselves are withheld with the transcripts."""
import json,numpy as np,pandas as pd
from sklearn.metrics import cohen_kappa_score
A=json.load(open("reorg_anno_A.json")); B=json.load(open("reorg_anno_B.json"))
H={h["id"]:h for h in json.load(open("reorg_anno_hidden.json"))}
ids=[i for i in A if i in B and i in H]; a=[A[i] for i in ids]; b=[B[i] for i in ids]
print(f"items: {len(ids)}")
print(f"inter-annotator: raw agreement={np.mean([x==y for x,y in zip(a,b)]):.2f}, "
      f"Cohen's kappa={cohen_kappa_score(a,b):.3f}")
cons=[x for x,y in zip(a,b) if x==y]
print("consensus typology:")
for k,v in pd.Series(cons).value_counts().items(): print(f"  {k:20s} {v:3d} ({100*v/len(cons):.0f}%)")
cl=lambda l:{"HANDOFF":"FLOOR","CO_CONSTRUCTION":"FLOOR","QA_CLARIFICATION":"QUESTION",
  "DECISION_CONVERGENCE":"DECISION","ENTRY_EXIT":"ENTRY","OTHER":"OTHER"}.get(l,"OTHER")
cr=lambda r:{"handoff":"FLOOR","opening":"FLOOR","roundrobin":"FLOOR","question":"QUESTION",
  "new_voice":"ENTRY","convergence":"DECISION","other/diffuse":"OTHER"}.get(r,"OTHER")
la=[cl(x) for x in a]; ra=[cr(H[i]["rule_primary"]) for i in ids]
print(f"LLM(coarse) vs rule-mechanism(coarse): agreement={np.mean([x==y for x,y in zip(la,ra)]):.2f}, "
      f"kappa={cohen_kappa_score(la,ra):.3f}  (form vs function: complementary layers)")
