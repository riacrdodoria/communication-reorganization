"""Figure: coding-free text measures aligned to the reorganization axis.
reorg_Z = (Z_entropy + Z_rmse - Z_det)/sqrt(3)  (entropy & RMSE up, %DET down = reorganization).
Color: CONTENT-based (independent of turn-taking) vs STRUCTURAL (turn-derived, partly mechanical)."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
df=pd.read_csv("triangulation_windows.csv")
MEAS={ # measure: (label, family)  family: C=content-independent, S=structural(turn-derived)
"sem_rec":("Semantic recurrence (TF-IDF)","C"),"coh":("Turn-to-turn coherence","C"),
"nov":("Novelty / topic-shift","C"),"lsm":("Language Style Matching (PT)","C"),
"connective":("Connective density (CohM-PT)","C"),"content_overlap":("Content-word overlap (CohM-PT)","C"),
"word_entropy":("Word entropy","C"),"ttr":("Type-token ratio","C"),
"mtld":("MTLD lexical diversity","C"),"hapax":("Hapax ratio","C"),
"turn_len":("Turn length (words)","S"),"n_turns":("Turns per window","S"),
"transition_entropy":("Speaker-transition entropy","S"),"latency":("Response latency","S")}
NPERM=500; rng=np.random.default_rng(0)
def z(a): a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def stouffer(feat,metric):
    zs=[]
    for mid,g in df.groupby("mid"):
        g=g.dropna(subset=[feat,metric]); n=len(g)
        if n<8: continue
        zx=z(g[feat].to_numpy(float)); zy=z(g[metric].to_numpy(float))
        if zx is None or zy is None: continue
        obs=float(zx@zy)/n
        sh=rng.integers(2,n-2,size=NPERM); idx=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[idx]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan
rows=[]
for f,(lab,fam) in MEAS.items():
    ze=stouffer(f,"entropy_g"); zd=stouffer(f,"det_g"); zr=stouffer(f,"rmse_g")
    reorgZ=(ze - zd + zr)/np.sqrt(3)
    rows.append(dict(feat=f,lab=lab,fam=fam,reorgZ=reorgZ,ze=ze,zd=zd,zr=zr))
R=pd.DataFrame(rows).sort_values("reorgZ")
R.to_csv("triangulation_Z.csv",index=False)
fig,ax=plt.subplots(figsize=(10,8.5))
col={"C":"#2E7D8C","S":"#9e9e9e"}
y=np.arange(len(R))
ax.barh(y,R.reorgZ,color=[col[f] for f in R.fam],edgecolor="black",lw=0.4,height=0.72)
ax.set_yticks(y); ax.set_yticklabels(R.lab,fontsize=10)
ax.axvline(0,color="black",lw=0.9)
for sv,xl in [(1.96,".05"),(3.29,".001")]:
    for s in (sv,-sv): ax.axvline(s,color="#bbb",ls=":",lw=0.8)
for i,(_,r) in enumerate(R.iterrows()):
    st='***' if abs(r.reorgZ)>3.29 else '**' if abs(r.reorgZ)>2.58 else '*' if abs(r.reorgZ)>1.96 else 'ns'
    ax.text(r.reorgZ+(0.6 if r.reorgZ>0 else -0.6),i,st,va="center",ha="left" if r.reorgZ>0 else "right",fontsize=8,color="#333")
ax.set_xlabel("← concentrated in STABLE periods      reorganization-aligned Stouffer Z      enriched at REORGANIZATION →",fontsize=10.5)
ax.set_title("Coding-free text measures track communication reorganization\n"
             "No human/LLM coding · 1949 windows · 34 meetings · within-meeting circular null",fontsize=12,pad=10)
tr=ax.get_xaxis_transform()
ax.text(0.27,1.02,"STABILITY / DELIBERATION",transform=ax.transAxes,ha="center",fontsize=10.5,fontweight="bold",color="#C0504D")
ax.text(0.76,1.02,"REORGANIZATION / COORDINATION",transform=ax.transAxes,ha="center",fontsize=10.5,fontweight="bold",color="#2E7D8C")
leg=[Patch(facecolor=col["C"],label="Content-based (independent of turn-taking)"),
     Patch(facecolor=col["S"],label="Structural (turn-derived — partly mechanical)")]
ax.legend(handles=leg,loc="lower right",fontsize=8.5,frameon=True)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig("fig_triangulation.png",dpi=200,bbox_inches="tight")
print("saved fig_triangulation.png")
print(R[["lab","fam","reorgZ"]].round(2).to_string(index=False))
