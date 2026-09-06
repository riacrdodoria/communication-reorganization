"""Episode-level analysis: is reorganization tied to TOPIC BOUNDARIES, and do episodes have an
internal ARC? Run on BOTH segmentations (LLM-8 high-quality, unsup-34 scale).
(a) Boundary-as-perturbation: entropy/%DET in ±30s of topic boundaries vs episode interior.
(b) Within-episode arc: entropy/%DET by normalized position (open/middle/close third)."""
import glob,os,numpy as np,pandas as pd
from scipy.stats import wilcoxon
GM="data/metrics_gorman_l8"; TXT="data/text_startup"; B=30
# NOTE 2026-09-05: LLM-8 indices for 2025.04.14 a/b shifted by -1 after the transcription-bot row was removed (remove_bot_rows.py).
llm={
"2024.10.14startup_a":[12,24,79,128,195,267,365,385,444,475],
"2024.12.09startup_a":[45,97,144,203,238,261,337,372,431,476,495],
"2025.02.24startup_a":[19,41,78,100,125,220,287,351],
"2025.04.14startup_a":[26,91,161,432,459,471],
"2024.10.14startup_b":[40,86,263,421,613,806],
"2024.12.16startup_b":[57,91,113,177,214,257,291,305,373,421,477,557,601],
"2025.02.24startup_b":[22,62,158,203,391],
"2025.04.14startup_b":[110,231,349,383]}
UE=pd.read_csv("episodes_unsup.csv")
def utt_to_sec(mid,idxs):
    df=pd.read_csv(f"{TXT}/{mid}_transcript.csv"); on=pd.to_numeric(df["onset_seconds"],errors="coerce").dropna().to_numpy()
    return [float(on[i]) for i in idxs if 0<=i<len(on)]
def boundaries_sec(mid,which):
    if which=="llm": return utt_to_sec(mid,llm[mid])
    sub=UE[UE.mid==mid].sort_values("utt_start"); return [float(s) for s in sub.sec_start.tolist()[1:]]
def episodes_sec(mid,which):
    if which=="llm":
        df=pd.read_csv(f"{TXT}/{mid}_transcript.csv"); on=pd.to_numeric(df["onset_seconds"],errors="coerce").dropna().to_numpy()
        bs=[0]+llm[mid]; es=bs[1:]+[len(on)]
        return [(float(on[a]),float(on[min(b,len(on)-1)])) for a,b in zip(bs,es)]
    sub=UE[UE.mid==mid].sort_values("utt_start"); return list(zip(sub.sec_start,sub.sec_end))

def run(which,mids):
    bd_e=[];bd_d=[]; arc={k:{0:[],1:[],2:[]} for k in ("ent","det")}
    for mid in mids:
        gp=f"{GM}/{mid}_gorman.csv"
        if not os.path.exists(gp): continue
        g=pd.read_csv(gp); sec=g["second"].to_numpy(); ent=g.entropy_g.to_numpy(float); det=g.det_g.to_numpy(float)
        bsec=boundaries_sec(mid,which)
        if not bsec: continue
        inb=np.zeros(len(sec),bool)
        for t in bsec: inb|=(np.abs(sec-t)<=B)
        if inb.sum()>=10 and (~inb).sum()>=10:
            bd_e.append(ent[inb].mean()-ent[~inb].mean()); bd_d.append(det[inb].mean()-det[~inb].mean())
        # arc
        for a,b in episodes_sec(mid,which):
            if b-a<90: continue
            m=(sec>=a)&(sec<=b)
            if m.sum()<10: continue
            pos=(sec[m]-a)/(b-a); e=ent[m]; d=det[m]
            for th in (0,1,2):
                sel=(pos>=th/3)&(pos<(th+1)/3 if th<2 else pos<=1.0001)
                if sel.sum()>0:
                    arc["ent"][th].append(e[sel].mean()); arc["det"][th].append(d[sel].mean())
    print(f"\n##### {which.upper()} segmentation ({len(mids)} meetings) #####")
    be=np.array(bd_e); bdd=np.array(bd_d)
    pe=wilcoxon(be).pvalue if len(be)>=8 else np.nan; pd_=wilcoxon(bdd).pvalue if len(bdd)>=8 else np.nan
    print(f"(a) BOUNDARY vs interior (±{B}s): Δentropy={be.mean():+.2f} (p={pe:.3f}) | Δ%DET={bdd.mean():+.2f} (p={pd_:.3f})")
    print(f"    {'entropy↑ + %DET↓ at boundaries = topic shift IS a reorganization' if be.mean()>0 and bdd.mean()<0 else 'mixed/none'}")
    print(f"(b) WITHIN-EPISODE ARC (mean over episodes, open→mid→close):")
    for k,lab in [("ent","entropy"),("det","%DET")]:
        v=[np.mean(arc[k][th]) for th in (0,1,2)]
        print(f"    {lab:8}: open={v[0]:.1f}  mid={v[1]:.1f}  close={v[2]:.1f}")
run("llm",list(llm))
run("unsup",sorted(UE.mid.unique()))
