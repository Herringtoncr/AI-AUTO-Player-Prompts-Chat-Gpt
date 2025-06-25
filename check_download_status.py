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
def load_player_ids(path):
    """Read your Players3.csv and return the set of all IDs."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["_ourLadsId"] for row in reader}

def extract_id(filename):
    """
    From a name like First_Last_123456_Team_html.txt,
    split on “_” and return the third element (the digits).
    Returns '123456' or None if the filename doesn’t follow that pattern.
    """
    parts = filename.split("_")
    # parts == ["First", "Last", "123456", "Team", "html.txt"]
    if len(parts) >= 3 and parts[2].isdigit():
        return parts[2]
    return None

def get_model_slug(path):
    """
    Read the file at `path`, look for data-message-model-slug="…",
    and return whatever’s between the quotes, or None if not found.
    """
    # 1) Read the full contents of the file into one string
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # 2) The exact marker we’re searching for
    marker = 'data-message-model-slug="'

    # 3) Find where that marker first appears
    start_idx = text.find(marker)
    if start_idx == -1:
        return None            # marker not present at all

    # 4) The real slug starts immediately after the marker
    slug_start = start_idx + len(marker)

    # 5) Find the next double-quote after slug_start
    slug_end = text.find('"', slug_start)
    if slug_end == -1:
        return None            # no closing quote

    # 6) Slice out just the slug text and return it
    return text[slug_start:slug_end]

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    player_ids = load_player_ids(PLAYERS_CSV)
    pending     = []  # (filename, reason)
    other       = []  # filenames

    # make sure we’re pointing at the right folder
    if not os.path.isdir(TARGET_FOLDER):
        print(f"❌ Cannot find snippet folder: {TARGET_FOLDER}")
        return

    for fn in os.listdir(TARGET_FOLDER):
        fp = os.path.join(TARGET_FOLDER, fn)
        if not os.path.isfile(fp):
            continue

        fid = extract_id(fn)
        if fid is None or fid not in player_ids:
            other.append(fn)
            continue

        size = os.path.getsize(fp)
        if size < MIN_SIZE_BYTES:
            pending.append((fn, "size<10KB"))
            continue

        slug = get_model_slug(fp)
        if slug != "o3":
            pending.append((fn, f"slug={slug or 'None'}"))
            continue
        # else: it’s a good file, skip it

    os.makedirs(TARGET_FOLDER, exist_ok=True)

    # Overwrite the pending‐files CSV
    with open(PENDING_CSV, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["filename", "reason"])
        w.writerows(pending)

    # Overwrite the “other‐machine” list
    with open(OTHER_TXT, "w", encoding="utf-8") as out:
        out.write("\n".join(other))

    print(f"✅ {len(pending)} pending → {PENDING_CSV}")
    print(f"⚠️ {len(other)} other-machine → {OTHER_TXT}")

if __name__ == "__main__":
    main()
