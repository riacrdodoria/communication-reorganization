"""Does each taxonomy category predict the BORDER perturbation vs the INTERIOR perturbation?
Reorganization events = rmse_g peaks (>mean+2.33SD). Each peak second is BORDER (within +/-30s of a
topic-episode start U EOS L10 stage onset) or INTERIOR. For every taxonomy category we take its window-
level density (90s codebooks) and compute, per meeting, the lift at border peaks vs baseline and at
interior peaks vs baseline (baseline = non-peak finite seconds). Across meetings: Wilcoxon + BH-FDR,
separately for border and interior, grouped by taxonomy. Writes reorg_taxonomy_borderinterior.csv."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
GM=Path("data/metrics_gorman_l8"); COD2=Path("data/codebooks2"); COD1=Path("data/codebooks")
TXT="data/text_startup"; TCRIT=2.33
CATS2=['arguable','converge','disagree','delim','nonarg','iam1','iam2','iam3','iam4','iam5',
       'disput','cumul','explor','bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin',
       'basksug','bsolid','btension','bagree','bdisagree','btensh','bantag']
CATS1=['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans',
       'coop','qset','qprop','directive','commissive','feedback']
TAX={**{c:"CACS" for c in ['arguable','converge','disagree','delim','nonarg']},
     **{c:"IAM" for c in ['iam1','iam2','iam3','iam4','iam5']},
     **{c:"Mercer" for c in ['disput','cumul','explor']},
     **{c:"Bales" for c in ['bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin','basksug','bsolid','btension','bagree','bdisagree','btensh','bantag']},
     **{c:"act4teams" for c in ['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans','coop']},
     **{c:"ISO" for c in ['qset','qprop','directive','commissive','feedback']}}
LABEL={'arguable':'arguable','converge':'convergent','disagree':'disagreement','delim':'delimiting','nonarg':'non-arguable',
 'iam1':'sharing','iam2':'dissonance','iam3':'negotiation','iam4':'testing','iam5':'agreement',
 'disput':'disputational','cumul':'cumulative','explor':'exploratory',
 'bgiveinfo':'gives info','bgiveopin':'gives opinion','bgivesug':'gives suggestion','baskinfo':'asks info',
 'baskopin':'asks opinion','basksug':'asks suggestion','bsolid':'solidarity','btension':'tension release',
 'bagree':'agrees','bdisagree':'disagrees','btensh':'shows tension','bantag':'antagonism',
 'namep':'names problem','linkp':'links problem','names':'names solution','links':'links solution',
 'linkc':'links consequence','cprod':'procedural','proact':'proactive','struct':'structuring',
 'ginfo':'gives info','ktrans':'knowledge transfer','coop':'cooperation',
 'qset':'set-question','qprop':'prop-question','directive':'directive','commissive':'commissive','feedback':'feedback'}
def load(folder):
    d={}
    for f in glob.glob(str(folder/"*_passA.json")):
        mid=os.path.basename(f).replace("_passA.json","")
        d[mid]={int(w["t"]):w for w in json.load(open(f))["windows"]}
    return d
c2=load(COD2); c1=load(COD1)
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
def l10_onsets(mid):
    f=f"data/l10_stages/{mid}.json"; tp=f"{TXT}/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return []
    d=json.load(open(f)); tx=pd.read_csv(tp); on=pd.to_numeric(tx.onset_seconds,errors="coerce").to_numpy()
    nt=[norm(t) for t in tx.text]; seg=[]; prev=0
    for st in d["stages"]:
        q=norm(st["quote"])[:60]; idx=None
        for i in range(prev,len(nt)):
            if q and q in nt[i]: idx=i;break
        if idx is None:
            for i in range(len(nt)):
                if q and q in nt[i]: idx=i;break
        if idx is not None: seg.append(float(on[idx]));prev=idx+1
    return seg
EP=pd.read_csv("episode_codes.csv")
bl=dict(); il=dict()
from collections import defaultdict
bl=defaultdict(list); il=defaultdict(list)
for f in sorted(glob.glob(str(GM/"*_gorman.csv"))):
    mid=os.path.basename(f).replace("_gorman.csv","")
    if mid not in c2: continue
    g=pd.read_csv(f); secs=g.second.to_numpy(); x=g.rmse_g.to_numpy(float)
    m=np.nanmean(x); sd=np.nanstd(x); peak=(x>m+TCRIT*sd); base=~peak & np.isfinite(x)
    bd=sorted(set(EP[EP.mid==mid].sec_start.tolist())|set(l10_onsets(mid)))
    if not bd: continue
    near=np.zeros(len(secs),bool)
    for b in bd: near|=(np.abs(secs-b)<=30)
    bpk=peak&near; ipk=peak&~near
    if bpk.sum()<6 or ipk.sum()<6 or base.sum()<20: continue
    win=lambda s:int(s//90*90)
    for cat in CATS2+CATS1:
        cd=c2[mid] if cat in CATS2 else c1.get(mid,{})
        dens=np.array([cd.get(win(s),{}).get(cat,0) for s in secs],float)
        if dens.sum()==0: continue
        b0=dens[base].mean()
        bl[cat].append(dens[bpk].mean()-b0); il[cat].append(dens[ipk].mean()-b0)
def test(d):
    rows=[]
    for cat in CATS2+CATS1:
        L=np.array(d.get(cat,[])); L=L[np.isfinite(L)]
        if len(L)<15: continue
        try: p=wilcoxon(L,zero_method="wilcox").pvalue
        except: p=1.0
        rows.append(dict(cat=cat,tax=TAX[cat],label=LABEL[cat],n=len(L),lift=L.mean(),pos=int((L>0).sum()),p=p))
    R=pd.DataFrame(rows); R["q"]=multipletests(R["p"],method="fdr_bh")[1]
    R["sig"]=R["q"].apply(lambda q:"***" if q<.001 else "**" if q<.01 else "*" if q<.05 else "")
    return R
B=test(bl).rename(columns={"lift":"border_lift","q":"border_q","sig":"border_sig","p":"border_p"})
I=test(il).rename(columns={"lift":"int_lift","q":"int_q","sig":"int_sig","p":"int_p"})
M=B.merge(I[["cat","int_lift","int_p","int_q","int_sig"]],on="cat",how="outer")
M=M.sort_values(["tax","cat"])
M.to_csv("reorg_taxonomy_borderinterior.csv",index=False)
TAXORDER=["CACS","IAM","Mercer","Bales","act4teams","ISO"]
print("Per-taxonomy association with BORDER vs INTERIOR perturbation (window-level lift; *FDR<.05)")
print("(↑ enriched at the perturbation, ↓ depressed; blank = n.s.)\n")
for t in TAXORDER:
    sub=M[M.tax==t]
    if not len(sub): continue
    print(f"== {t} ==")
    print(f"   {'category':20s} {'BORDER':>14s}   {'INTERIOR':>14s}")
    for _,r in sub.iterrows():
        bs=f"{r.border_lift:+.3f}{r.border_sig}" if pd.notna(r.border_lift) else "   --"
        is_=f"{r.int_lift:+.3f}{r.int_sig}" if pd.notna(r.int_lift) else "   --"
        print(f"   {r.label:20s} {bs:>14s}   {is_:>14s}")
    print()
nb=int((M.border_q<.05).sum()); ni=int((M.int_q<.05).sum())
print(f"significant (FDR<.05): BORDER {nb}/{M.border_q.notna().sum()} categories; INTERIOR {ni}/{M.int_q.notna().sum()}.")
