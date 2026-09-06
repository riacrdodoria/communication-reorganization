"""Figure: floor/turn-taking/centrality measures aligned to the reorganization axis.
reorg_Z = (Z_entropy - Z_%DET + Z_RMSE)/sqrt(3). Color by family."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
d=pd.read_csv("floor_windows.csv")
MEAS={ # measure:(label, family)
"part_entropy":("Participation entropy  (≈ Gorman entropy)","P"),
"top_share":("Top-speaker share (quant. dominance)","P"),
"gini_words":("Gini participation (words)","P"),
"gini_turns":("Gini participation (turns)","P"),
"n_active":("Active speakers / window","F"),
"turnlen_disp":("Turn-length dispersion (Edelsky F1>F2)","F"),
"net_central":("Network degree centralization","N"),
"eig_central":("Max eigenvector centrality","N"),
"inout_asym":("Dyadic transition asymmetry (who follows whom)","I")}
FAMCOL={"P":"#2E7D8C","F":"#e6ab02","N":"#7570b3","I":"#d95f02"}
FAMLAB={"P":"Participation / dominance","F":"Floor regime (Edelsky F1/F2)","N":"Network centrality","I":"Influence / sequential dominance"}
NP=500; rng=np.random.default_rng(0)
def z(a): a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stf(feat,metric):
    zs=[]
    for mid,gg in d.groupby("mid"):
        gg=gg.dropna(subset=[feat,metric]); n=len(gg)
        if n<8: continue
        zx=z(gg[feat].to_numpy(float)); zy=z(gg[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n; sh=rng.integers(2,n-2,size=NP); ix=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[ix]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
rows=[]
for f,(lab,fam) in MEAS.items():
    rz=(stf(f,"entropy_g")-stf(f,"det_g")+stf(f,"rmse_g"))/np.sqrt(3)
    rows.append(dict(feat=f,lab=lab,fam=fam,reorgZ=rz))
R=pd.DataFrame(rows).sort_values("reorgZ")
fig,ax=plt.subplots(figsize=(10.5,7))
y=np.arange(len(R))
ax.barh(y,R.reorgZ,color=[FAMCOL[f] for f in R.fam],edgecolor="black",lw=0.4,height=0.72)
ax.set_yticks(y); ax.set_yticklabels(R.lab,fontsize=10)
ax.axvline(0,color="black",lw=0.9)
for s in (1.96,3.29,-1.96,-3.29): ax.axvline(s,color="#ccc",ls=":",lw=0.8)
for i,(_,r) in enumerate(R.iterrows()):
    stt='***' if abs(r.reorgZ)>3.29 else '**' if abs(r.reorgZ)>2.58 else '*' if abs(r.reorgZ)>1.96 else 'ns'
    ax.text(r.reorgZ+(0.7 if r.reorgZ>0 else -0.7),i,stt,va="center",ha="left" if r.reorgZ>0 else "right",fontsize=8,color="#333")
ax.set_xlabel("reorganization-aligned Stouffer Z",fontsize=11)
ax.text(0.25,1.03,"STABILITY = Edelsky F1\n(singly-developed floor)",transform=ax.transAxes,ha="center",fontsize=10,fontweight="bold",color="#C0504D")
ax.text(0.76,1.03,"REORGANIZATION = Edelsky F2\n(collaborative floor)",transform=ax.transAxes,ha="center",fontsize=10,fontweight="bold",color="#2E7D8C")
ax.set_title("Communication reorganization = floor equalizing & de-centralizing (F1→F2)\n"
             "9 coding-free floor/centrality measures · 1949 windows · 34 meetings",fontsize=12,pad=34)
leg=[Patch(facecolor=c,label=FAMLAB[k]) for k,c in FAMCOL.items()]
ax.legend(handles=leg,loc="lower right",fontsize=8.5,frameon=True)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig("fig_floor.png",dpi=200,bbox_inches="tight")
print("saved fig_floor.png")
PY_END = None
