"""Cross the 6 taxonomies (41 categories) with the EOS L10 agenda stages.

For each meeting we reconstruct the L10 stage second-boundaries (same quote->second mapping as
l10_analysis.py), assign every fine topic-episode to the stage that contains its sec_start, and aggregate
taxonomy counts. Two questions:
  (1) Which content (taxonomy categories) dominates each L10 stage?  -> rate per utterance, pooled.
  (2) Does content differ between the procedural REVIEW stages (scorecard/rock/todo) and IDS?
      -> per-meeting paired Wilcoxon on category rate, BH-FDR across categories.
Writes l10_taxonomy_rates.csv and l10_taxonomy_review_vs_ids.csv."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

TXT="data/text_startup"
STAGE_ORDER=["segue","scorecard","rock_review","headlines","todo","ids","conclude"]
REVIEW=["scorecard","rock_review","todo"]

# 41 category code -> (taxonomy, readable label)
LAB={
 "arguable":("CACS","arguable"),"converge":("CACS","convergent"),"disagree":("CACS","disagreement"),
 "delim":("CACS","delimiting"),"nonarg":("CACS","non-arguable"),
 "iam1":("IAM","sharing/comparing"),"iam2":("IAM","dissonance"),"iam3":("IAM","negotiation"),
 "iam4":("IAM","testing"),"iam5":("IAM","agreement/application"),
 "disput":("Mercer","disputational"),"cumul":("Mercer","cumulative"),"explor":("Mercer","exploratory"),
 "bgiveinfo":("Bales","gives information"),"bgiveopin":("Bales","gives opinion"),
 "bgivesug":("Bales","gives suggestion"),"baskinfo":("Bales","asks information"),
 "baskopin":("Bales","asks opinion"),"basksug":("Bales","asks suggestion"),
 "bsolid":("Bales","solidarity"),"btension":("Bales","tension release"),"bagree":("Bales","agrees"),
 "bdisagree":("Bales","disagrees"),"btensh":("Bales","shows tension"),"bantag":("Bales","antagonism"),
 "qset":("ISO","set-question"),"qprop":("ISO","propositional-q"),"directive":("ISO","directive"),
 "commissive":("ISO","commissive"),"feedback":("ISO","feedback"),
 "namep":("act4teams","names problem"),"linkp":("act4teams","links problem"),
 "names":("act4teams","names solution"),"links":("act4teams","links solution"),
 "linkc":("act4teams","links to consequence"),"cprod":("act4teams","procedural"),
 "proact":("act4teams","proactive"),"struct":("act4teams","structuring"),
 "ginfo":("act4teams","gives information"),"ktrans":("act4teams","knowledge transfer"),
 "coop":("act4teams","cooperation"),
}
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()

def stage_bounds(mid):
    """Return list of (stage, s0, s1) second-intervals for a meeting, or None."""
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
    bounds=[s[1] for s in seg]+[float(np.nanmax(on))+5]
    return [(seg[k][0],seg[k][1],bounds[k+1]) for k in range(len(seg))]

E=pd.read_csv("episode_codes.csv")
CATS=[c for c in LAB if c in E.columns]
# assign each episode to its L10 stage by sec_start
E["l10"]=None
for mid,g in E.groupby("mid"):
    sb=stage_bounds(mid)
    if not sb: continue
    for i,r in g.iterrows():
        for name,s0,s1 in sb:
            if s0<=r["sec_start"]<s1: E.at[i,"l10"]=name; break
E=E[E["l10"].notna()].copy()
print(f"episodes assigned to an L10 stage: {len(E)} across {E.mid.nunique()} meetings")

# (1) content profile per stage: pooled rate per utterance (count / total utterances in stage)
prof={}
for st in STAGE_ORDER:
    s=E[E.l10==st]
    if not len(s): continue
    nut=s["n_utt"].sum()
    prof[st]={c:100*s[c].sum()/nut for c in CATS}
prof=pd.DataFrame(prof).reindex(columns=[c for c in STAGE_ORDER if c in prof])
prof.index=[f"{LAB[c][0]}:{LAB[c][1]}" for c in prof.index]
prof.round(2).to_csv("l10_taxonomy_rates.csv")
print("\n=== Top content per L10 stage (rate per 100 utterances; top 4) ===")
for st in prof.columns:
    top=prof[st].sort_values(ascending=False).head(4)
    print(f"  {st:11s}: "+", ".join(f"{i} {v:.0f}" for i,v in top.items()))

# (2) review vs IDS per category, per-meeting paired rate (count / n_utt within the stage group)
def stage_rate(g,cats):  # per meeting, rate per utt for a set of stages
    nut=g["n_utt"].sum()
    return {c:(g[c].sum()/nut if nut else np.nan) for c in cats}
rows=[]
for mid,g in E.groupby("mid"):
    rv=g[g.l10.isin(REVIEW)]; iv=g[g.l10=="ids"]
    if not len(rv) or not len(iv): continue
    rr=stage_rate(rv,CATS); ir=stage_rate(iv,CATS)
    rows.append((mid,rr,ir))
print(f"\nmeetings with both review and IDS episodes: {len(rows)}")
res=[]
for c in CATS:
    rv=np.array([r[1][c] for r in rows]); iv=np.array([r[2][c] for r in rows])
    ok=~(np.isnan(rv)|np.isnan(iv))
    if ok.sum()<8 or np.allclose(rv[ok],iv[ok]): continue
    try: p=wilcoxon(rv[ok],iv[ok],zero_method="wilcox").pvalue
    except Exception: continue
    res.append(dict(cat=c,tax=LAB[c][0],label=LAB[c][1],n=int(ok.sum()),
        review=100*np.nanmean(rv[ok]),ids=100*np.nanmean(iv[ok]),
        delta=100*(np.nanmean(rv[ok])-np.nanmean(iv[ok])),p=p))
R=pd.DataFrame(res)
if len(R):
    R["q"]=multipletests(R["p"],method="fdr_bh")[1]
    R["sig"]=R["q"].apply(lambda q:"***" if q<.001 else "**" if q<.01 else "*" if q<.05 else "")
    R=R.sort_values("delta",ascending=False)
    R.round(3).to_csv("l10_taxonomy_review_vs_ids.csv",index=False)
    show=R[["tax","label","review","ids","delta","p","q","sig"]].copy()
    print("\n=== Content that distinguishes REVIEW (scorecard/rock/todo) vs IDS (rate/100 utt; BH-FDR) ===")
    print("  -- enriched in REVIEW --")
    print(show[show.delta>0].head(10).to_string(index=False))
    print("  -- enriched in IDS --")
    print(show[show.delta<0].sort_values("delta").head(10).to_string(index=False))
    print(f"\nsignificant after BH-FDR: {(R['q']<.05).sum()}/{len(R)} categories")
