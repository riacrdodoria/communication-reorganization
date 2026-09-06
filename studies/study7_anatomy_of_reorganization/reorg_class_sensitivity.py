"""Sensitivity of the INTERIOR_HANDOFF / INTERIOR_OTHER split to the handoff rule (2026-09-05).
Five reasonable variants of (anchor, window, weight); canonical = centre/30/turns (Study 7)."""
import glob, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reorg_events as RE
import importlib.util
GM="data/metrics_gorman_l8"; TXT="data/text_startup"
# reuse Study 7's boundary builder
spec=importlib.util.spec_from_file_location("sig", "reorg_signature.py")
EP=pd.read_csv("episode_codes.csv")
exec(open("reorg_signature.py").read().split("EP=pd.read_csv")[0].replace("import reorg_events as RE",""))  # defines norm, l10_onsets, dom
VARIANTS={"canonical (centre,30s,turns)":dict(anchor="center",window=30,weight="turns"),
          "centre,30s,words":dict(anchor="center",window=30,weight="words"),
          "onset,15s,words (old S9)":dict(anchor="onset",window=15,weight="words"),
          "onset,30s,turns":dict(anchor="onset",window=30,weight="turns"),
          "centre,15s,turns":dict(anchor="center",window=15,weight="turns")}
rows=[]
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    g=pd.read_csv(f); sec=g.second.to_numpy(float); rm=g.rmse_g.to_numpy(float); ok=~np.isnan(rm)
    if ok.sum()<60: continue
    thr=np.nanmean(rm[ok])+2.33*np.nanstd(rm[ok]); evsec=sec[ok][rm[ok]>thr]
    bd=sorted(set(EP[EP.mid==mid].sec_start.tolist())|set(l10_onsets(mid)))
    tx=pd.read_csv(f"{TXT}/{mid}_transcript.csv"); on=pd.to_numeric(tx.onset_seconds,errors="coerce")
    okt=on.notna(); on=on[okt].to_numpy(float); sp=tx.speaker_id.astype(str).to_numpy()[okt.to_numpy()]
    nw=np.array([max(1,len(str(t).split())) for t in tx.text.to_numpy()[okt.to_numpy()]],float)
    for e in RE.cluster_events(evsec):
        r=dict(mid=mid,center=float(np.mean(e)))
        for name,kw in VARIANTS.items(): r[name]=RE.classify(e,bd,on,sp,nw,**kw)[0]
        rows.append(r)
D=pd.DataFrame(rows); names=list(VARIANTS)
print(f"events: {len(D)}  TRANSITION: {(D[names[0]]=='TRANSITION').sum()} (identical across variants by construction)")
I=D[D[names[0]]!="TRANSITION"]
print(f"\ninterior events: {len(I)}")
out=[]
for n in names:
    h=int((I[n]=="INTERIOR_HANDOFF").sum()); agree=float((I[n]==I[names[0]]).mean())
    print(f"  {n:32s}: HANDOFF {h:3d} / OTHER {len(I)-h:3d}   agreement with canonical = {100*agree:.0f}%")
    out.append(dict(variant=n,n_handoff=h,n_other=len(I)-h,agreement_with_canonical=agree))
pd.DataFrame(out).to_csv("reorg_class_sensitivity.csv",index=False); print("wrote reorg_class_sensitivity.csv")
