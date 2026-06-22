"""Map L10 stage quotes -> utterance index -> second, label the metric series by L10 stage, and test
where reorganization concentrates across stages. Runs on whatever data/l10_stages/*.json exist."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
GM="data/metrics_gorman_l8"; TXT="data/text_startup"
STAGE_ORDER=["segue","scorecard","rock_review","headlines","todo","ids","conclude"]
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
rows=[]; coverage=[]
for f in sorted(glob.glob("data/l10_stages/*.json")):
    mid=os.path.basename(f).replace(".json","")
    d=json.load(open(f)); tp=f"{TXT}/{mid}_transcript.csv"
    if not os.path.exists(tp): continue
    tx=pd.read_csv(tp); on=pd.to_numeric(tx["onset_seconds"],errors="coerce").to_numpy()
    ntx=[norm(t) for t in tx["text"]]
    # map each stage quote to first utterance index >= previous, by substring
    seg=[]; prev=0
    for st in d["stages"]:
        q=norm(st["quote"])[:60]; idx=None
        for i in range(prev,len(ntx)):
            if q and q in ntx[i]: idx=i; break
        if idx is None:  # fallback: search whole transcript
            for i in range(len(ntx)):
                if q and q in ntx[i]: idx=i; break
        if idx is not None:
            seg.append((st["name"],idx,float(on[idx]))); prev=idx+1
    if not seg: continue
    coverage.append((mid,len(seg),len(d["stages"])))
    g=pd.read_csv(f"{GM}/{mid}_gorman.csv"); sec=g["second"].to_numpy()
    rm=g.rmse_g.to_numpy(float); rmean,rsd=np.nanmean(rm),np.nanstd(rm)
    peak=rm>rmean+2.33*rsd
    bounds=[s[2] for s in seg]+[float(on[-1])+5]
    for k,(name,uidx,s0) in enumerate(seg):
        s1=bounds[k+1]; m=(sec>=s0)&(sec<s1)
        if m.sum()<3: continue
        rows.append(dict(mid=mid,stage=name,dur_s=s1-s0,
            entropy=g.entropy_g[m].mean(),det=g.det_g[m].mean(),rmse=g.rmse_g[m].mean(),
            reorg_rate=100*peak[m].mean(),secs=int(m.sum())))
P=pd.DataFrame(rows)
print("=== L10 mapping coverage (meetings done) ===")
for mid,n,tot in coverage: print(f"  {mid}: {n}/{tot} stages mapped")
print(f"\n=== Reorganization by L10 stage (pooled, weighted by seconds; {P.mid.nunique()} meetings) ===")
def wmean(g,c): return np.average(g[c],weights=g["secs"])
agg=P.groupby("stage").apply(lambda g:pd.Series({
    "n_mtg":g.mid.nunique(),"%_of_meeting":100*g.secs.sum()/P.secs.sum(),
    "mean_entropy":wmean(g,"entropy"),"mean_%DET":wmean(g,"det"),"reorg_rate%":wmean(g,"reorg_rate")})).reindex(STAGE_ORDER).dropna(how="all")
print(agg.round(1).to_string())
print("\n(Hypothesis: IDS = most reorganized — highest entropy / lowest %DET / highest reorg-rate vs the review stages.)")
P.to_csv("l10_stage_metrics.csv",index=False)
