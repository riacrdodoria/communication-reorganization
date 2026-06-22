"""Convergence of the three segmentations: fixed windows, data-driven topic episodes, theory-driven EOS
L10 stages. Two tests:
 (A) Do the data-driven episode TYPES land on the theory-driven L10 STAGES they should? -> type x stage
     cross-tab, chi-square + Cramer's V; plus where each type concentrates.
 (B) Do topic-episode BOUNDARIES co-locate with L10 stage boundaries above chance? -> fraction of L10
     boundaries with an episode boundary within +/-TOL s, observed vs within-meeting circular-shift null.
Writes l10_convergence_typestage.csv."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import chi2_contingency, wilcoxon

TXT="data/text_startup"; STAGE_ORDER=["segue","scorecard","rock_review","headlines","todo","ids","conclude"]
TOL=15.0; NPERM=500; rng=np.random.default_rng(0)
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
def stage_bounds(mid):
    f=f"data/l10_stages/{mid}.json"; tp=f"{TXT}/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return None
    d=json.load(open(f)); tx=pd.read_csv(tp)
    on=pd.to_numeric(tx["onset_seconds"],errors="coerce").to_numpy(); ntx=[norm(t) for t in tx["text"]]
    seg=[]; prev=0
    for st in d["stages"]:
        q=norm(st["quote"])[:60]; idx=None
        for i in range(prev,len(ntx)):
            if q and q in ntx[i]: idx=i; break
        if idx is None:
            for i in range(len(ntx)):
                if q and q in ntx[i]: idx=i; break
        if idx is not None: seg.append((st["name"],float(on[idx]))); prev=idx+1
    if not seg: return None
    end=float(np.nanmax(on))+5
    bounds=[s[1] for s in seg]+[end]
    return [(seg[k][0],seg[k][1],bounds[k+1]) for k in range(len(seg))], end

E=pd.read_csv("episode_codes.csv")
# ---- characterize episode types by position + reorganization, give descriptive labels ----
tp=E.groupby("type").agg(n=("ep","size"),pos=("pos","mean"),entropy=("entropy_g","mean"),
                         det=("det_g","mean")).sort_values("pos")
order=list(tp.index)  # by within-meeting position
NAMES=["opening / procedural","status / info-sharing","problem / debate","solution exploration","closing / socio-emotional"]
lab={t:NAMES[i] if i<len(NAMES) else f"type{t}" for i,t in enumerate(order)}
tp["label"]=[lab[t] for t in tp.index]
print("=== Episode types (data-driven), ordered by within-meeting position ===")
print(tp.assign(pct=(100*tp.n/tp.n.sum()).round(0)).round({"pos":2,"entropy":1,"det":1})[["label","n","pct","pos","entropy","det"]].to_string())

# ---- assign each episode to its L10 stage ----
E["l10"]=None; epb={}; l10b={}; durs={}
for mid,g in E.groupby("mid"):
    sb=stage_bounds(mid)
    if not sb: continue
    segs,end=sb; durs[mid]=end
    for i,r in g.iterrows():
        for name,s0,s1 in segs:
            if s0<=r["sec_start"]<s1: E.at[i,"l10"]=name; break
    epb[mid]=sorted(v for v in g["sec_start"].tolist() if v>5)            # episode boundaries
    l10b[mid]=sorted(s0 for _,s0,_ in segs if s0>5)                       # L10 stage onsets
A=E[E.l10.notna()].copy(); A["lab"]=A["type"].map(lab)

# ---- (A) type x stage association ----
ct=pd.crosstab(A["lab"],A["l10"]).reindex(columns=[s for s in STAGE_ORDER if s in A.l10.unique()]).reindex(NAMES).fillna(0)
chi2,p,dof,_=chi2_contingency(ct.values)
n=ct.values.sum(); V=np.sqrt(chi2/(n*(min(ct.shape)-1)))
print(f"\n=== (A) Episode-type x L10-stage association ===\nchi2={chi2:.0f}, dof={dof}, p={p:.2e}, Cramer's V={V:.3f}, n={int(n)} episodes")
print("\nRow-normalized (% of each episode type that falls in each stage):")
print((100*ct.div(ct.sum(1),axis=0)).round(0).to_string())
# where does each stage's time come from? and the key directional check
print("\nColumn-normalized (% of each stage made of each episode type):")
print((100*ct.div(ct.sum(0),axis=1)).round(0).to_string())
ct.to_csv("l10_convergence_typestage.csv")

# ---- (B) boundary co-location vs circular-shift null ----
def recall(refs,cands,end):  # fraction of refs with a cand within TOL
    if not len(refs): return np.nan
    return np.mean([any(abs(c-r)<=TOL for c in cands) for r in refs])
obs=[]; nul=[]
for mid in l10b:
    if mid not in epb or not l10b[mid] or not epb[mid]: continue
    end=durs[mid]; r=recall(l10b[mid],epb[mid],end)
    nr=[]
    for _ in range(NPERM):
        sh=rng.uniform(0,end); cand=[(b+sh)%end for b in epb[mid]]
        nr.append(recall(l10b[mid],cand,end))
    obs.append(r); nul.append(np.mean(nr))
obs=np.array(obs); nul=np.array(nul)
W=wilcoxon(obs,nul).pvalue
print(f"\n=== (B) Topic-episode boundaries co-locate with L10 stage onsets (+/-{TOL:.0f}s) ===")
print(f"meetings={len(obs)}  observed recall={obs.mean():.2f}  circular-shift null={nul.mean():.2f}  "
      f"lift={obs.mean()-nul.mean():+.2f}  paired Wilcoxon p={W:.2e}")
