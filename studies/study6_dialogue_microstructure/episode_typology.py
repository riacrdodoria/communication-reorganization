"""Episode typology: cluster the 970 fine episodes by their 41-category taxonomy profile to discover
TYPES of discussion. k-means on z-scored densities; k by silhouette. Characterize each type by its
defining categories + mean entropy/%DET + within-meeting position + developmental trend."""
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
df=pd.read_csv("episode_codes.csv")
CATS="arguable converge disagree delim nonarg iam1 iam2 iam3 iam4 iam5 disput cumul explor bgiveinfo bgiveopin bgivesug baskinfo baskopin basksug bsolid btension bagree bdisagree btensh bantag qset qprop directive commissive feedback namep linkp names links linkc cprod proact struct ginfo ktrans coop".split()
D=df[CATS].div(df["n_utt"].clip(lower=1),axis=0)               # densities
D=D.loc[:,D.sum()>0]
X=StandardScaler().fit_transform(D.values)
best=None
for k in range(3,8):
    lab=KMeans(k,n_init=10,random_state=0).fit_predict(X); s=silhouette_score(X,lab)
    print(f"k={k}: silhouette={s:.3f}")
    if best is None or s>best[1]: best=(k,s,lab)
k,s,lab=best; df["type"]=lab
print(f"\nChosen k={k} (silhouette {s:.3f}). Episode types:\n")
# within-meeting normalized position + developmental order
df["pos"]=df.groupby("mid")["ep"].transform(lambda e:e/e.max() if e.max()>0 else 0)
mids=sorted(df.mid.unique())
gm=df.assign(meanD=D.mean(1))
for t in range(k):
    sub=df[df.type==t]; Dt=D.loc[sub.index]
    # defining categories = highest mean z-density
    z=(Dt.mean()-D.mean())/D.std()
    top=z.sort_values(ascending=False).head(6)
    print(f"=== TYPE {t}  (n={len(sub)} episodes, {100*len(sub)/len(df):.0f}%) ===")
    print(f"   defining categories: "+", ".join(f"{c}(+{v:.1f}σ)" for c,v in top.items()))
    print(f"   mean entropy={sub.entropy_g.mean():.1f}  %DET={sub.det_g.mean():.1f}  "
          f"within-meeting pos={sub.pos.mean():.2f}  n_utt={sub.n_utt.mean():.0f}")
df.to_csv("episode_codes.csv",index=False)
print("\n(pos≈0=meeting opening, ≈1=closing. Type labels are descriptive; saved 'type' to episode_codes.csv)")
