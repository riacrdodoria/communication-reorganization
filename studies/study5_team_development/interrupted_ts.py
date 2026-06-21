"""Interrupted time-series (segmented regression, Wagner et al. 2002) for the mid-Jan->Feb GAP.
NOTE: the gap is a real ~4-6 week CALENDAR gap (a: 13 Jan->24 Feb; b: 13 Jan->10 Feb) but its CAUSE is
UNCERTAIN (summer pause vs uncollected meetings) — so b2 is NOT interpreted as a behavioral perturbation.
Model:  Y = b0 + b1*time + b2*post + b3*time_after + e
  time       = elapsed weeks since first meeting (calendar time)
  post       = 0 before gap, 1 after (gap = between meeting 10 and 11, both teams)
  time_after = elapsed weeks since the gap date, 0 before
  b1 = pre-trend; b2 = LEVEL change at the gap; b3 = SLOPE change after.
Per team + pooled (team fixed effect). OLS by hand (no statsmodels)."""
import numpy as np,pandas as pd
from scipy.stats import t as tdist
S=pd.read_csv("longitudinal_panel.csv")
T=pd.read_csv("longitudinal_taxonomy_panel.csv")[["mid","coord_comp","delib_comp","balance"]]
P=S.merge(T,on="mid",how="left")
P["dt"]=pd.to_datetime(P["dt"])
# elapsed weeks + break vars per team (break = date of meeting with week index 11)
def add_time(g):
    g=g.sort_values("week").copy()
    t0=g["dt"].iloc[0]
    g["time"]=(g["dt"]-t0).dt.days/7.0
    bdate=g.loc[g["week"]==11,"dt"].iloc[0]
    g["post"]=(g["week"]>=11).astype(float)
    g["time_after"]=np.where(g["post"]==1,(g["dt"]-bdate).dt.days/7.0,0.0)
    return g
P=P.groupby("team",group_keys=False).apply(add_time)

def ols(X,y):
    XtXi=np.linalg.inv(X.T@X); beta=XtXi@X.T@y; resid=y-X@beta
    n,k=X.shape; s2=resid@resid/(n-k); se=np.sqrt(np.diag(s2*XtXi))
    tval=beta/se; p=2*tdist.sf(np.abs(tval),n-k); return beta,se,p,n-k

VARS=[("mean_entropy","Mean entropy"),("mean_det","Mean %DET"),("reorg_rate","Reorg-event rate"),
      ("eig_central","Network centrality"),("top_share","Top-speaker share"),
      ("coord_comp","Coordination comp"),("delib_comp","Deliberation comp"),("balance","Coord−Delib balance")]
def stars(p): return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else ''

print("=== PER-TEAM segmented regression: LEVEL change (b2) and SLOPE change (b3) at the break ===")
print(f"{'variable':20}| {'team':9}| {'pre-trend b1':>12}| {'LEVEL Δ b2':>14}| {'SLOPE Δ b3':>14}")
for v,lab in VARS:
    for tm,g in P.groupby("team"):
        g=g.dropna(subset=[v])
        X=np.column_stack([np.ones(len(g)),g["time"],g["post"],g["time_after"]]); y=g[v].to_numpy(float)
        b,se,p,df=ols(X,y)
        print(f"{lab:20}| {tm:9}| {b[1]:>+8.3f}{stars(p[1]):<4}| {b[2]:>+9.3f}{stars(p[2]):<5}| {b[3]:>+9.3f}{stars(p[3]):<5}")
    print()

print("=== POOLED (both teams, team fixed effect): break LEVEL (b2) & SLOPE (b3) ===")
print(f"{'variable':20}| {'pre-trend':>11}| {'LEVEL Δ b2':>14}| {'SLOPE Δ b3':>14}")
P["team_b"]=(P["team"]=="startup_b").astype(float)
for v,lab in VARS:
    g=P.dropna(subset=[v])
    X=np.column_stack([np.ones(len(g)),g["time"],g["post"],g["time_after"],g["team_b"]]); y=g[v].to_numpy(float)
    b,se,p,df=ols(X,y)
    print(f"{lab:20}| {b[1]:>+7.3f}{stars(p[1]):<4}| {b[2]:>+9.3f}{stars(p[2]):<5}| {b[3]:>+9.3f}{stars(p[3]):<5}")
print("\n(b2 LEVEL Δ = the immediate jump at the break BEYOND trend = the perturbation effect.")
print(" b3 SLOPE Δ = change in trend after the break. b1 = underlying developmental trend.)")
