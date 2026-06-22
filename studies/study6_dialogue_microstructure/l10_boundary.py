"""L10 stage transitions as natural perturbations. For each meeting, label the second-by-second metric
series with whether it is within +/-WIN s of an L10 stage onset (boundary zone) vs interior. Paired
Wilcoxon across meetings on entropy and %DET (boundary - interior). Then isolate the IDS-entry transition
(the move into the problem-solving block). Mirrors the topic-episode boundary-as-perturbation test."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import wilcoxon
GM="data/metrics_gorman_l8"; TXT="data/text_startup"; WIN=30.0
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
def stage_onsets(mid):
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
    return seg or None

rows=[]; idsrows=[]
for f in sorted(glob.glob("data/l10_stages/*.json")):
    mid=os.path.basename(f).replace(".json","")
    seg=stage_onsets(mid)
    if not seg or not os.path.exists(f"{GM}/{mid}_gorman.csv"): continue
    g=pd.read_csv(f"{GM}/{mid}_gorman.csv"); sec=g["second"].to_numpy(float)
    onsets=[s0 for _,s0 in seg if s0>WIN]                       # skip meeting-start
    if not onsets: continue
    near=np.zeros(len(sec),bool)
    for s0 in onsets: near|=(np.abs(sec-s0)<=WIN)
    if near.sum()<3 or (~near).sum()<3: continue
    rows.append(dict(mid=mid,
        e_b=g.entropy_g[near].mean(),e_i=g.entropy_g[~near].mean(),
        d_b=g.det_g[near].mean(),d_i=g.det_g[~near].mean()))
    # IDS-entry only
    ids_on=[s0 for nm,s0 in seg if nm=="ids" and s0>WIN]
    if ids_on:
        m=np.zeros(len(sec),bool)
        for s0 in ids_on: m|=(np.abs(sec-s0)<=WIN)
        if m.sum()>=3 and (~m).sum()>=3:
            idsrows.append(dict(mid=mid,e_b=g.entropy_g[m].mean(),e_i=g.entropy_g[~m].mean(),
                d_b=g.det_g[m].mean(),d_i=g.det_g[~m].mean()))
R=pd.DataFrame(rows); I=pd.DataFrame(idsrows)
def rep(df,tag):
    de=df.e_b-df.e_i; dd=df.d_b-df.d_i
    pe=wilcoxon(df.e_b,df.e_i).pvalue; pd_=wilcoxon(df.d_b,df.d_i).pvalue
    s=lambda p:"***" if p<.001 else "**" if p<.01 else "*" if p<.05 else "ns"
    print(f"\n{tag} (n={len(df)}, +/-{WIN:.0f}s of stage onset vs interior):")
    print(f"  entropy: boundary {df.e_b.mean():.1f} vs interior {df.e_i.mean():.1f}  Delta={de.mean():+.2f}  p={pe:.3g} {s(pe)}")
    print(f"  %DET:    boundary {df.d_b.mean():.1f} vs interior {df.d_i.mean():.1f}  Delta={dd.mean():+.2f}  p={pd_:.3g} {s(pd_)}")
print("=== L10 stage transitions as perturbations ===")
rep(R,"ALL L10 stage onsets")
if len(I): rep(I,"IDS-entry only")
R.to_csv("l10_boundary_panel.csv",index=False)
