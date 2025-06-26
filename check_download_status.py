#!/usr/bin/env python3
import os
import csv
import socket
import re
from automation.config_loader import config

# ─── CONFIG ───────────────────────────────────────────────────
PROJECT_ROOT   = os.path.dirname(__file__)

# where your HTML/snippet .txt files actually land
OF = config.get("output_folder", "txt")
if os.path.isabs(OF):
    TARGET_FOLDER = OF
else:
    TARGET_FOLDER = os.path.join(PROJECT_ROOT, OF)

PLAYERS_CSV    = config["csv_path"]           # e.g. "csv/Players3.csv"
MIN_SIZE_BYTES = 10 * 1024                    # 10 KB

machine_name   = socket.gethostname()
PENDING_CSV    = os.path.join(
    TARGET_FOLDER,
    f"pending_files_{machine_name}.csv"
)
OTHER_TXT      = os.path.join(
    TARGET_FOLDER,
    f"anothermachine_files_{machine_name}.txt"
)

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def extract_id(filename):
    parts = filename.split("_")
    if len(parts) >= 3 and parts[2].isdigit():
        return parts[2]
    return None

def get_model_slug(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    marker = 'data-message-model-slug="'
    start_idx = text.find(marker)
    if start_idx == -1:
        return None
    slug_start = start_idx + len(marker)
    slug_end = text.find('"', slug_start)
    if slug_end == -1:
        return None
    return text[slug_start:slug_end]

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    # 1) Build an ordered list of IDs directly from Players3.csv
    csv_path = PLAYERS_CSV if os.path.isabs(PLAYERS_CSV) \
               else os.path.join(PROJECT_ROOT, PLAYERS_CSV)
    ordered_ids = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ordered_ids.append(row["_ourLadsId"])

    pending = []  # will hold (filename, reason) in CSV order
    other   = []  # will hold any files not matched to those IDs

    # ensure the snippet folder exists
    if not os.path.isdir(TARGET_FOLDER):
        print(f"❌ Cannot find snippet folder: {TARGET_FOLDER}")
        return

    # 2) List all files in the folder once
    folder_files = [
        fn for fn in os.listdir(TARGET_FOLDER)
        if os.path.isfile(os.path.join(TARGET_FOLDER, fn))
    ]

    # 3) Iterate in the exact order of the CSV
    for fid in ordered_ids:
        # look for First_Last_<fid>_... .txt
        pattern = re.compile(rf".*_{fid}_.*\.txt$")
        matches = [fn for fn in folder_files if pattern.match(fn)]
        if not matches:
            pending.append((f"(ID {fid})", "missing file"))
            continue

        fn = matches[0]
        fp = os.path.join(TARGET_FOLDER, fn)

        size = os.path.getsize(fp)
        if size < MIN_SIZE_BYTES:
            pending.append((fn, "size<10KB"))
            continue

        slug = get_model_slug(fp)
        if slug != "o3":
            pending.append((fn, f"slug={slug or 'None'}"))
            continue
        # else: good file, skip it

    # ─── NEW: collect any “other” files not in pending ────────────────────────
    processed = {fn for fn, _ in pending}
    unmatched = sorted(set(folder_files) - processed)
    other.extend(unmatched)

    # ensure output folder exists (safe‐guard; folder already checked above)
    os.makedirs(TARGET_FOLDER, exist_ok=True)

    # 4) Overwrite the pending‐files CSV
    with open(PENDING_CSV, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["filename", "reason"])
        w.writerows(pending)

    # 5) Overwrite the “other‐machine” list
    with open(OTHER_TXT, "w", encoding="utf-8") as out:
        out.write("\n".join(other))

    print(f"✅ {len(pending)} pending → {PENDING_CSV}")
    print(f"⚠️ {len(other)} other-machine → {OTHER_TXT}")

if __name__ == "__main__":
    main()
