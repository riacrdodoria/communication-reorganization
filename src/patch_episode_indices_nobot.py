"""Phase 1 remediation (2026-09-05), companion to remove_bot_rows.py.

The episode segmentations (data/episodes_fine.csv, episodes_unsup.csv) store UTTERANCE INDICES into
the transcripts. Removing the BOT row shifts every later index by -1 in the 10 affected meetings. The bot
line never sits on an episode boundary (verified), so second-based boundaries (sec_start/sec_end) and the
LLM episode codings are unchanged; only the indices, the n_utt of the containing episode, and the
per-episode metric means (entropy_g/det_g/rmse_g, recomputed from the regenerated metrics) change.

Idempotent via a marker file. Originals backed up with suffix .with_bot.bak.
"""
import os, shutil
import numpy as np, pandas as pd

LSH = os.path.expanduser("~/lsh-work")
MARK = f"{LSH}/data/.episodes_patched_nobot"
if os.path.exists(MARK):
    print("already patched; nothing to do"); raise SystemExit

roles = pd.read_csv(f"{LSH}/study9_initiators/data/speaker_roles_verified.csv")
bot_idx = {}
for _, r in roles[roles.role == "BOT"].iterrows():
    tx = pd.read_csv(f"{LSH}/data/text_startup_with_bot/{r.mid}_transcript.csv")
    bot_idx[r.mid] = int(tx.index[tx.speaker_id.astype(str) == str(r.raw_id)][0])

def shift(df, start_col, end_col):
    for mid, i in bot_idx.items():
        m = df.mid == mid
        assert not ((df.loc[m, start_col] == i) | (df.loc[m, end_col] == i)).any(), (mid, "bot on boundary")
        contains = m & (df[start_col] < i) & (df[end_col] > i)
        assert contains.sum() == 1, (mid, contains.sum())
        df.loc[contains, "n_utt"] -= 1
        df.loc[m & (df[start_col] > i), start_col] -= 1
        df.loc[m & (df[end_col] > i), end_col] -= 1
    return df

for path, sc, ec in [(f"{LSH}/data/episodes_fine.csv", "utt_start", "utt_end"),
                     (f"{LSH}/episodes_unsup.csv", "utt_start", "utt_end")]:
    shutil.copy(path, path + ".with_bot.bak")
    df = shift(pd.read_csv(path), sc, ec)
    df.to_csv(path, index=False); print("patched", path)

# episode_codes.csv: n_utt of containing episode, and per-episode metric means for the 10 meetings
path = f"{LSH}/episode_codes.csv"; shutil.copy(path, path + ".with_bot.bak")
ec = pd.read_csv(path); ef = pd.read_csv(f"{LSH}/data/episodes_fine.csv")
for mid in bot_idx:
    g = pd.read_csv(f"{LSH}/data/metrics_gorman_l8/{mid}_gorman.csv")
    for k in ec.index[ec.mid == mid]:
        r = ec.loc[k]
        n_new = int(ef[(ef.mid == mid) & (ef.ep == r.ep)].n_utt.iloc[0])
        ec.loc[k, "n_utt"] = n_new
        m = (g.second >= r.sec_start) & (g.second <= r.sec_end)
        if m.sum():
            ec.loc[k, "entropy_g"] = g.entropy_g[m].mean()
            ec.loc[k, "det_g"] = g.det_g[m].mean()
            ec.loc[k, "rmse_g"] = np.nanmean(g.rmse_g[m]) if g.rmse_g[m].notna().any() else np.nan
ec.to_csv(path, index=False); print("patched", path)
open(MARK, "w").write("patched 2026-09-05\n")
