"""Strict Gorman/Grimm reimplementation of communication-reorganization metrics.
- Binary multi-speaker team states (overlaps allowed), 2 Hz.
- offset = onset + 0.5*n_words (2 words/sec interpolation, Gorman 2020/2025).
- entropy = Shannon over team states / log2(2^n_speakers) *100  (%MaxEntropy).
- %DET = recurrence determinism of the team-state series (Lmin=2).
- RMSE = nonlinear-prediction (method of analogues) on the %DET series, eps=3 %DET, horizon=20s.
All on a 60 s sliding window, 1 s output step. Mechanical (turn-taking only)."""
from __future__ import annotations
import sys, numpy as np, pandas as pd
from pathlib import Path

HZ=2; DT=1.0/HZ; WIN_S=60; STEP_S=1; LMIN=2; RMSE_EPS=3.0; RMSE_H=20

def build_states(df):
    sp=sorted(int(s) for s in df['speaker_id'].dropna().unique())
    idx={s:i for i,s in enumerate(sp)}
    on=[]; off=[]; who=[]
    for r in df.itertuples(index=False):
        try: o=float(r.onset_seconds)
        except: continue
        nw=max(1,len(str(r.text).split()))
        on.append(o); off.append(o+0.5*nw); who.append(idx[int(r.speaker_id)])
    maxt=max(off) if off else 0.0
    nt=int(np.ceil(maxt/DT))+1
    M=np.zeros((len(sp),nt),dtype=np.int8)
    grid=np.arange(nt)*DT
    for o,f,w in zip(on,off,who):
        a=int(np.floor(o/DT)); b=int(np.ceil(f/DT))
        M[w,a:b]=1
    # team state integer (bitmask over speakers)
    state=np.zeros(nt,dtype=np.int64)
    for i in range(len(sp)): state|=(M[i].astype(np.int64)<<i)
    return state, len(sp)

def det_window(seg, lmin=LMIN):
    n=seg.size
    if n<2: return np.nan
    eq=seg[:,None]==seg[None,:]
    iu=np.triu_indices(n,k=1)
    rec=int(eq[iu].sum())
    if rec==0: return 0.0
    tot=0
    for off in range(1,n):
        d=np.diagonal(eq,offset=off)
        run=0
        for v in d:
            if v: run+=1
            else:
                if run>=lmin: tot+=run
                run=0
        if run>=lmin: tot+=run
    return 100.0*tot/rec

def rmse_analogues(series, eps=RMSE_EPS, h=RMSE_H):
    x=np.asarray(series,float); n=x.size; out=np.full(n,np.nan)
    for i in range(n-h):
        if np.isnan(x[i]): continue
        cand=np.arange(0,i-h)
        if cand.size==0: continue
        m=np.abs(x[cand]-x[i])<=eps
        nb=cand[m & ~np.isnan(x[cand])]
        if nb.size==0: continue
        preds=np.vstack([x[j:j+h+1] for j in nb])
        pred=np.nanmean(preds,axis=0); target=x[i:i+h+1]
        out[i]=np.sqrt(np.nanmean((target-pred)**2))
    return out

def compute(path, lmin=LMIN):
    df=pd.read_csv(path)
    state,nsp=build_states(df)
    nt=state.size; w=int(WIN_S/DT); step=int(STEP_S/DT); half=w//2
    maxbits=np.log2(2**nsp)
    secs=[]; ent=[]; det=[]
    for c in range(half, nt-half, step):
        seg=state[c-half:c+half+1]
        _,cnt=np.unique(seg,return_counts=True); p=cnt/cnt.sum()
        H=-(p*np.log2(p)).sum()
        secs.append(round(c*DT)); ent.append(100.0*H/maxbits); det.append(det_window(seg,lmin))
    det=np.array(det)
    rmse=rmse_analogues(det)
    return pd.DataFrame({"second":secs,"entropy_g":ent,"det_g":det,"rmse_g":rmse}), nsp

if __name__=="__main__":
    import time
    p=sys.argv[1] if len(sys.argv)>1 else "data/text_startup/2024.10.14startup_a_transcript.csv"
    t0=time.time(); out,nsp=compute(p); dt=time.time()-t0
    print(f"speakers={nsp}  windows={len(out)}  time={dt:.1f}s")
    print(out.describe().loc[['min','mean','max']].round(2).to_string())
    print(out.head(3).to_string(index=False))

def run_all():
    import glob,os
    outdir=Path("data/metrics_gorman"); outdir.mkdir(parents=True,exist_ok=True)
    for f in sorted(glob.glob("data/text_startup/*_transcript.csv")):
        mid=os.path.basename(f).replace("_transcript.csv","")
        out,nsp=compute(f)
        out.to_csv(outdir/f"{mid}_gorman.csv",index=False)
        print(f"  {mid}: nsp={nsp} win={len(out)} entMean={out.entropy_g.mean():.1f} detMean={out.det_g.mean():.1f} rmseMax={out.rmse_g.max():.2f}",flush=True)
