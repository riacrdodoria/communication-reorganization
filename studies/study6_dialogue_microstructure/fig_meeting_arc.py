"""Figure: the meeting ARC — episode-type composition across within-meeting position + %DET overlay.
Stacked area = fraction of each of the 5 discussion types per position decile; line = mean %DET."""
import numpy as np,pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
df=pd.read_csv("episode_codes.csv")
LAB={3:"Opening / procedural Q&A",1:"Status / info-sharing",4:"Problem / debate",
     2:"Solution exploration",0:"Closing / socio-emotional"}
ORDER=[3,1,4,2,0]   # by mean within-meeting position (arc order)
COL={3:"#7570b3",1:"#2E7D8C",4:"#d95f02",2:"#1b9e77",0:"#e6ab02"}
nb=10; df["bin"]=np.minimum((df["pos"]*nb).astype(int),nb-1)
comp=df.groupby(["bin","type"]).size().unstack(fill_value=0)
comp=comp.div(comp.sum(1),axis=0)
x=(np.arange(nb)+0.5)/nb
det=df.groupby("bin")["det_g"].mean()
fig,ax=plt.subplots(figsize=(11,6.5))
ax.stackplot(x,*[comp.get(t,pd.Series(0,index=range(nb))).reindex(range(nb),fill_value=0).values for t in ORDER],
             colors=[COL[t] for t in ORDER],labels=[LAB[t] for t in ORDER],alpha=.85)
ax.set_xlabel("within-meeting position  (0 = opening → 1 = closing)",fontsize=11)
ax.set_ylabel("episode-type composition",fontsize=11); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax2=ax.twinx()
ax2.plot(x,det.reindex(range(nb)).values,"o-",color="black",lw=2,ms=5,label="mean %DET")
ax2.set_ylabel("mean %DET (↑ = more stable / monologic)",fontsize=11)
ax.set_title("The meeting arc — discussion types across within-meeting position\n"
             "open → status → problem → solution → close (970 fine episodes, 34 meetings)",fontsize=12.5,pad=10)
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax.legend(h1+h2,l1+l2,loc="upper center",bbox_to_anchor=(0.5,-0.12),ncol=3,fontsize=9,frameon=True)
ax.spines[['top']].set_visible(False); ax2.spines[['top']].set_visible(False)
plt.tight_layout(); plt.savefig("fig_meeting_arc.png",dpi=190,bbox_inches="tight")
print("saved fig_meeting_arc.png")
