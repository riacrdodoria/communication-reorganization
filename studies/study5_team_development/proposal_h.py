"""Proposal H — does within-meeting REORGANIZATION CAPACITY change with team maturity (micro->macro)?
Per-meeting capacity proxies (robust to the 60s/1s sliding-window smoothing):
  entropy_sd, det_sd   = dynamic RANGE along the F1<->F2 axis (flexibility)
  reorg_rate           = % RMSE peaks (event frequency)
  valley_depth         = mean depth of %DET valleys (in within-meeting SD units; amplitude)
  episode_dur          = mean duration (s) of %DET-valley episodes (shorter = faster recovery)
Trend over the 17 weekly meetings per team (Mann-Kendall), replicated across teams.
NOTE: avoids 1s autocorrelation/recovery metrics (confounded by the sliding window)."""
import glob,os,re,numpy as np,pandas as pd
from datetime import date
from scipy.stats import kendalltau
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
GM="data/metrics_gorman_l8"
def parse(mid):
    m=re.match(r"(\d{4})\.(\d{2})\.(\d{2})(.+)",mid); y,mo,d,t=m.groups(); return t,date(int(y),int(mo),int(d))
def episodes(mask):
    durs=[]; run=0
    for v in mask:
        if v: run+=1
        elif run>0: durs.append(run); run=0
    if run>0: durs.append(run)
    return durs
rows=[]
for f in sorted(glob.glob(GM+"/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    g=pd.read_csv(f); team,dt=parse(mid)
    ent=g.entropy_g.to_numpy(float); det=g.det_g.to_numpy(float); rmse=g.rmse_g.to_numpy(float)
    dm,ds=np.nanmean(det),np.nanstd(det); rm,rs=np.nanmean(rmse),np.nanstd(rmse)
    valley=det<dm-2.33*ds; peak=rmse>rm+2.33*rs
    durs=episodes(valley)
    rows.append(dict(mid=mid,team=team,dt=dt,
        entropy_sd=np.nanstd(ent), det_sd=ds,
        reorg_rate=100*np.nanmean(peak),
        valley_depth=np.nanmean((dm-det[valley])/ds) if valley.any() else 0.0,
        episode_dur=np.mean(durs) if durs else 0.0))
P=pd.DataFrame(rows); P["dt"]=pd.to_datetime(P["dt"])
P=P.sort_values(["team","dt"]).reset_index(drop=True)
P["week"]=P.groupby("team").cumcount()+1
P.to_csv("proposal_h_panel.csv",index=False)

VARS=[("entropy_sd","Entropy range (flexibility)"),("det_sd","%DET range (flexibility)"),
      ("reorg_rate","Reorg-event rate"),("valley_depth","Valley depth (amplitude)"),
      ("episode_dur","Episode duration (recovery)")]
print("=== Proposal H: capacity proxies over 17 weeks (Kendall tau per team; * p<.05) ===")
print(f"{'capacity proxy':30}| {'startup_a':>13} | {'startup_b':>13} | both dir?")
for v,lab in VARS:
    cells={}
    for tm,sub in P.groupby("team"):
        sub=sub.dropna(subset=[v]); cells[tm]=kendalltau(sub["week"],sub[v])
    a,b=cells["startup_a"],cells["startup_b"]
    same="YES"+("*" if (a[1]<.05 and b[1]<.05) else "") if np.sign(a[0])==np.sign(b[0]) else "no"
    print(f"{lab:30}| tau={a[0]:>+5.2f}{'*' if a[1]<.05 else ' '} | tau={b[0]:>+5.2f}{'*' if b[1]<.05 else ' '} | {same}")
print("\n(Interpretation: range/amplitude DOWN = consolidation/rigidification; episode_dur DOWN = faster recovery.)")

fig,axes=plt.subplots(2,3,figsize=(14,7.5)); axes=axes.ravel()
col={"startup_a":"#2E7D8C","startup_b":"#d95f02"}
for ax,(v,lab) in zip(axes,VARS):
    for tm,sub in P.groupby("team"):
        sub=sub.sort_values("week"); ax.plot(sub["week"],sub[v],"o-",color=col[tm],ms=4,lw=1.4,label=tm,alpha=.85)
    ax.set_title(lab,fontsize=10); ax.set_xlabel("meeting (week)",fontsize=8); ax.tick_params(labelsize=7)
axes[0].legend(fontsize=8); axes[-1].axis("off")
fig.suptitle("Proposal H — within-meeting reorganization capacity over 17 weekly meetings (2 teams)",fontsize=12)
plt.tight_layout(rect=[0,0,1,0.97]); plt.savefig("fig_proposal_h.png",dpi=170,bbox_inches="tight")
print("saved proposal_h_panel.csv, fig_proposal_h.png")
