#!/usr/bin/env python3
"""Which onset-only approximation of the team state best reproduces the standard representation?
Ground truth: Gorman et al. (2020) archival sessions with hand-coded onsets and offsets (per-second speaker
series, silence = 0). From those sessions we keep only what an ASR transcript would give (utterance onset,
speaker, text) and rebuild the series four ways:
  LSH          speaker holds the floor until the next onset
  LSH-WD       speaker holds for onset + 0.5 s per word (Gorman's 2 words/s rule), then silence
  LSH-CAP3     speaker holds at most 3 s, then silence
  LSH-CAP10    speaker holds at most 10 s, then silence
Each variant is compared with the true standard series on entropy, %DET (L_min 8), RMSE, event overlap and
level bias, with the Paper 1 parameters. Output: results/lsh_variants_team.csv, lsh_variants_summary.csv."""
import os, sys, re, glob, numpy as np, pandas as pd
from pathlib import Path
from importlib import util
sys.path.insert(0, os.path.expanduser("~/lsh-work"))
spec = util.spec_from_file_location("ar", os.path.expanduser("~/lsh-work/study1_lsh_validation/lsh_convergent_current_params.py"))
src = open(spec.origin).read().split("inv = pd.read_csv")[0]; ns = {}; exec(src, ns)
metrics, events, overlap, rr, HZ = ns["metrics"], ns["events"], ns["overlap"], ns["r"], ns["HZ"]
CAN = Path(os.path.expanduser("~/lsh-work/data/processed/canonical"))
RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/lsh-work/data/archival_raw")  # Gorman et al. (2020) workbooks, not distributed
OUT = Path(os.path.expanduser("~/lsh-work/study1_lsh_validation/results"))
WPS = 0.5  # seconds per word

def norm(c): return str(c).strip().lower().replace("\n", " ")
def text_per_second(path):
    df = pd.read_excel(path, sheet_name=pd.ExcelFile(path).sheet_names[0]); cols = {norm(c): c for c in df.columns}
    sec = cols.get("team epoch") or cols.get("epoch"); dia = cols.get("dialogue") or cols.get("dialog")
    if sec is None or dia is None: return None
    t = df[[sec, dia]].copy(); t.columns = ["second", "text"]; t["second"] = pd.to_numeric(t.second, errors="coerce")
    t = t.dropna(subset=["second"]); t["second"] = t.second.round().astype(int); t["text"] = t.text.fillna("").astype(str)
    return t.groupby("second").text.apply(lambda s: " ".join(x for x in s if x and x.lower() != "nan")).reset_index()

def utterances(std, text_by_sec, sec0):
    """runs of identical non-zero speaker in the true series -> (onset_index, speaker, words)"""
    utts = []; i = 0; n = std.size
    while i < n:
        if std[i] == 0: i += 1; continue
        j = i
        while j + 1 < n and std[j + 1] == std[i]: j += 1
        words = sum(len(re.findall(r"\w+", text_by_sec.get(sec0 + k, ""))) for k in range(i, j + 1))
        utts.append((i, int(std[i]), max(1, words))); i = j + 1
    return utts

def build(utts, n, kind):
    s = np.zeros(n, dtype=np.int64)
    for k, (a, who, w) in enumerate(utts):
        nxt = utts[k + 1][0] if k + 1 < len(utts) else n
        if kind == "LSH": b = nxt
        elif kind == "LSH-WD": b = min(nxt, a + int(np.ceil(WPS * w)))
        elif kind == "LSH-CAP3": b = min(nxt, a + 3)
        elif kind == "LSH-CAP10": b = min(nxt, a + 10)
        s[a:max(b, a + 1)] = who
    return s

inv = pd.read_csv(CAN / "inventory.csv"); inv = inv[inv.status.astype(str).eq("processed")]
raw_files = {Path(p).stem: p for p in glob.glob(f"{RAW}/*/*.xls*")}
rows = []; EXCERPT = ("J11T1-OutputsT4",); excerpt = {}
for row in inv.itertuples(index=False):
    tid = str(row.team_id); stem = {"J5S2a": "J5S2BatchUtt-CzP0"}.get(tid, tid)
    if stem not in raw_files: print("no raw file for", tid); continue
    can = pd.read_csv(CAN / f"{tid}.csv"); std = pd.to_numeric(can.speaker_id, errors="coerce").fillna(0).astype(int).to_numpy(); sec0 = int(can.second.iloc[0])
    tps = text_per_second(raw_files[stem]); tmap = dict(zip(tps.second, tps.text)) if tps is not None else {}
    first = int(np.argmax(std > 0)); std = std[first:]; sec0 += first; n = std.size; nsp = len(set(std[std > 0]))
    utts = utterances(std, tmap, sec0); n_words = sum(u[2] for u in utts)
    ms = metrics(std, nsp + 1); ea = events(ms.rmse.to_numpy())
    for kind in ["LSH", "LSH-WD", "LSH-CAP3", "LSH-CAP10"]:
        v = build(utts, n, kind); states = nsp + (1 if (v == 0).any() else 0); mv = metrics(v, states); eb = events(mv.rmse.to_numpy()); oa, ob = overlap(ea, eb)
        rows.append(dict(team_id=tid, domain=row.domain, variant=kind, n_utts=len(utts), words_per_utt=n_words / max(1, len(utts)), silence_true=100 * (std == 0).mean(), silence_variant=100 * (v == 0).mean(),
                         r_entropy=rr(ms.entropy.to_numpy(), mv.entropy.to_numpy()), r_det=rr(ms.det.to_numpy(), mv.det.to_numpy()), r_rmse=rr(ms.rmse.to_numpy(), mv.rmse.to_numpy()),
                         bias_entropy=mv.entropy.mean() - ms.entropy.mean(), bias_det=mv.det.mean() - ms.det.mean(), n_events_std=len(ea), n_events_var=len(eb), events_std_matched=oa, events_var_matched=ob,
                         mean_entropy_std=ms.entropy.mean(), mean_entropy_var=mv.entropy.mean(), mean_det_std=ms.det.mean(), mean_det_var=mv.det.mean(),
                         mean_rmse_std=np.nanmean(ms.rmse.to_numpy()), mean_rmse_var=np.nanmean(mv.rmse.to_numpy())))
        if tid == EXCERPT[0]: excerpt[kind] = v; excerpt["standard"] = std
        r0 = rows[-1]; print(f"{tid:22s} {kind:9s} sil {r0['silence_true']:4.1f}->{r0['silence_variant']:4.1f}  r ent {r0['r_entropy']:.3f} det {r0['r_det']:.3f} rmse {r0['r_rmse']:.3f}  bias ent {r0['bias_entropy']:+.1f}  events {len(ea)}/{len(eb)} matched {oa:.2f}", flush=True)
T = pd.DataFrame(rows); T.to_csv(OUT / "lsh_variants_team.csv", index=False)
if excerpt: np.savez(OUT / "lsh_variants_excerpt.npz", **excerpt)  # 2 Hz speaker codes of one surgical session, for the representation diagram
S = T.groupby(["variant"]).agg(n=("team_id", "count"), r_entropy=("r_entropy", "mean"), r_det=("r_det", "mean"), r_rmse=("r_rmse", "mean"), events_std_matched=("events_std_matched", "mean"), events_var_matched=("events_var_matched", "mean"),
                              bias_entropy=("bias_entropy", "mean"), bias_det=("bias_det", "mean"), silence_variant=("silence_variant", "mean"), silence_true=("silence_true", "mean")).round(3)
S.to_csv(OUT / "lsh_variants_summary.csv"); print("\nSUMMARY (15 sessions)\n" + S.to_string())
Sd = T.groupby(["domain", "variant"])[["r_entropy", "r_det", "r_rmse", "events_std_matched"]].mean().round(3); print("\nBY DOMAIN\n" + Sd.to_string()); print("VARIANTS_DONE")
