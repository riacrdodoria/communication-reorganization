"""Phase 1 remediation (2026-09-05): remove the transcription-tool announcement line (role == BOT in
study9_initiators/data/speaker_roles_verified.csv) from the canonical transcripts so that it is no longer
counted as a speaker by gorman_reimpl.build_states (nsp) or by any transcript-based analysis.

- Originals are preserved once in data/text_startup_with_bot/ (never overwritten if present).
- The previously published metrics are preserved once in data/metrics_gorman_l8_with_bot/.
- DEVICE rows (a real participant on a shared device) are KEPT.
- Idempotent: running twice removes nothing the second time.
"""
import os, shutil, glob
import pandas as pd

LSH = os.path.expanduser("~/lsh-work")
TXT = f"{LSH}/data/text_startup"
BAK = f"{LSH}/data/text_startup_with_bot"
MET = f"{LSH}/data/metrics_gorman_l8"
METBAK = f"{LSH}/data/metrics_gorman_l8_with_bot"

if not os.path.isdir(BAK):
    shutil.copytree(TXT, BAK); print(f"backed up transcripts -> {BAK}")
if not os.path.isdir(METBAK):
    shutil.copytree(MET, METBAK); print(f"backed up metrics -> {METBAK}")

roles = pd.read_csv(f"{LSH}/study9_initiators/data/speaker_roles_verified.csv")
bot = roles[roles.role == "BOT"]
assert (bot.n_utt == 1).all(), bot
total = 0
for _, r in bot.iterrows():
    f = f"{TXT}/{r.mid}_transcript.csv"
    tx = pd.read_csv(f)
    before = len(tx)
    tx = tx[tx.speaker_id.astype(str) != str(r.raw_id)]
    removed = before - len(tx)
    if removed:
        tx.to_csv(f, index=False)
    total += removed
    print(f"{r.mid}: raw_id {r.raw_id} -> removed {removed} row(s); {before}->{len(tx)}; ids now {sorted(tx.speaker_id.unique())}")
print(f"total removed: {total} (expected {len(bot)} on first run, 0 afterwards)")
