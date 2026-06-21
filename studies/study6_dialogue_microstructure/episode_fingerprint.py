"""Episode-level taxonomy fingerprint of reorganization (clean fine-episode units, not 90s windows).
For each category: density = count/n_utt per episode. Within-meeting Pearson(density, reorg metric)
across episodes, combined across 34 meetings via Fisher-z (meeting = unit). BH-FDR.
Reorganization = entropy↑ / %DET↓ → a category 'at reorganization' has +r with entropy, −r with %DET."""
import numpy as np,pandas as pd
from scipy.stats import norm
df=pd.read_csv("episode_codes.csv")
TAX={"CACS":["arguable","converge","disagree","delim","nonarg"],
"Bales":["bgiveinfo","bgiveopin","bgivesug","baskinfo","baskopin","basksug","bsolid","btension","bagree","bdisagree","btensh","bantag"],
"ISO":["qset","qprop","directive","commissive","feedback"],
"act4teams":["proact","struct","coop","cprod","ginfo","ktrans","namep","names","linkp","links","linkc"],
"IAM":["iam1","iam2","iam3","iam4","iam5"],"Mercer":["disput","cumul","explor"]}
ALL=[c for cs in TAX.values() for c in cs]
for c in ALL: df[c+"_d"]=df[c]/df["n_utt"].clip(lower=1)
def fisher(metric):
    out={}
    for c in ALL:
        rs=[]
        for mid,g in df.groupby("mid"):
            g=g.dropna(subset=[c+"_d",metric])
            if len(g)<6 or g[c+"_d"].std()==0 or g[metric].std()==0: continue
            r=np.corrcoef(g[c+"_d"],g[metric])[0,1]
            rs.append(np.clip(r,-0.999,0.999))
        if len(rs)<10: out[c]=(np.nan,np.nan,0); continue
        z=np.arctanh(rs); Z=np.mean(z)*np.sqrt(len(rs)); out[c]=(np.tanh(np.mean(z)),Z,len(rs))
    return out
ENT=fisher("entropy_g"); DET=fisher("det_g")
def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
ps=[2*norm.sf(abs(ENT[c][1])) if np.isfinite(ENT[c][1]) else 1 for c in ALL]
q=dict(zip(ALL,bh(ps)))
print("Episode-level fingerprint — r(category density, ENTROPY) across episodes (meeting=unit, Fisher-z).")
print("+r = category ENRICHED in high-entropy (reorganization) episodes; −r = in low-entropy (stability).\n")
nsig=0
for tx,cs in TAX.items():
    print(f"-- {tx} --")
    for c in sorted(cs,key=lambda c:-(ENT[c][0] if np.isfinite(ENT[c][0]) else -9)):
        rE,ZE,nE=ENT[c]; rD=DET[c][0]
        if not np.isfinite(rE): print(f"   {c:11} (n/a)"); continue
        star="*" if q[c]<.05 else ""
        if q[c]<.05: nsig+=1
        arrow="REORG" if rE>0 else "STABLE"
        print(f"   {c:11} r_ent={rE:+.2f} (Z={ZE:+.1f}{star})  r_det={rD:+.2f}  -> {arrow if q[c]<.05 else 'ns'}")
print(f"\n{nsig}/{len(ALL)} categories significant (FDR) at the episode level.")
