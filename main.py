#!/usr/bin/env python3
import check_download_status
from scheduler import run_with_shift
# 1) run the scanner to refresh pending_files_<host>.csv
check_download_status.main()

import os
import csv
import time
import pdb
import pyperclip
import socket

from automation.config_loader import config  # loads settings from config/config.yaml
from automation.macro_runner import execute_macro

# ─── Setup paths ──────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(__file__)

# CSV of all players
CSV_REL_PATH = config.get('csv_path', 'csv/players3.csv')
CSV_FILE     = os.path.join(PROJECT_ROOT, *CSV_REL_PATH.replace('\\', '/').split('/'))

# Where snippets are saved
OF = config.get('output_folder', 'txt')
SAVE_DIR = OF if os.path.isabs(OF) else os.path.join(PROJECT_ROOT, OF)
os.makedirs(SAVE_DIR, exist_ok=True)

# Load pending-files list
HOST         = socket.gethostname()
PENDING_CSV  = os.path.join(SAVE_DIR, f"pending_files_{HOST}.csv")
pending_files = set()
if os.path.exists(PENDING_CSV):
    with open(PENDING_CSV, newline='', encoding='utf-8') as pf:
        reader = csv.DictReader(pf)
        pending_files = {row['filename'] for row in reader}

# ─── Prompt template ────────────────────────────────────────────────
PROMPT_TEMPLATE = config.get('prompt_template', '''
You are a CFB beat writer.

TASK  
Produce an *ultra-condensed NCAAF résumé* for *[FIRST] [LAST] – [TEAM] [POSITION]*.

FORMAT & RULES  
• Use tight bullet points (one line each).  
• Begin every line with either:  
  – an exact date in M-D-YY: format (e.g., 4-26-22:) *or*  
  – a season tag using the last two digits (e.g., 22:).  
• Include *only high-value facts*:  
  – recruiting rank / commit year  
  – starting / bench status *& number of starts*  
  – major injuries *& return dates*  
  – transfer-portal moves (destination *and documented reason* – include a source link)  
  – awards (MVP, All-Conference, etc.)  
  – current roster / depth-chart status & outlook  
  – practice-reps status (first-team or second-team) from current-year spring/fall workouts  
• *No fluff, adjectives, or analysis*—just facts.  
• *Append* a reliable supporting article link at the end of each bullet (in parentheses).  
• Keep every bullet ≤ 25 words.

*Finish with these five required bullets (in order):*  
• *[POS] room:* snapshot of immediate competition (QB, WR, RB, OL, DL, LB, DB)  
• *2025 outlook:* one-line odds of starting or role expectation  
• *Practice reps:* specify “mostly 1st-team” or “mostly 2nd-team” with source link  
• *Eligibility:* years remaining (e.g., “3 seasons left through 2027”)  
• *NIL:* estimated Name-Image-Likeness valuation for the season (e.g., “NIL: $230k”)

*Summary* (≤ 45 words)  
• Begin with YL X (years of eligibility left, e.g., YL 3)  
• Use 2-digit years (e.g., 25, 24) and common team abbreviations (BAMA, PITT, UW, etc.)  
• Retain star-rating format (e.g., 4⭐)  
• State current-year practice status (1st-team or 2nd-team)  
• Cite clear, sourced reason for any portal move (no hearsay)  
• *No links* inside the summary.

---

### No-link version  
After the résumé above, create a second block titled *“No-link version:”*.  
• *First row:* [PLAYER NAME] – [POSITION] (plain text, no team, no links).  
• Then repeat the entire résumé *including the Summary, in the **same bullet format, **but delete all links*.  
• Do *not* alter content or order; only remove the URLs and surrounding parentheses.
''')  # truncated for brevity

# ─── Helpers ────────────────────────────────────────────────────────
def read_players(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield {
                'id':       row.get('_ourLadsId', '').strip(),
                'first':    row.get('_firstName', '').strip(),
                'last':     row.get('_lastName', '').strip(),
                'position': row.get('_position', '').strip(),
                'team':     row.get('_teamName', '').strip(),
            }

def save_player_html(file_name):
    copied_text = pyperclip.paste()
    if not copied_text.strip():
        print(f"❌ Clipboard empty—skipping save for {file_name}")
        return
    path = os.path.join(SAVE_DIR, file_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(copied_text)
    print(f"✅ Content saved to {path}")

# ─── Main loop ─────────────────────────────────────────────────────
def main():
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV not found: {CSV_FILE}")
        return

    if not pending_files:
        print("🚀 No pending files to process. Exiting.")
        return

    for idx, player in enumerate(read_players(CSV_FILE), start=1):
        first = player['first']
        last  = player['last']
        pid   = player['id']
        pos   = player['position']
        team  = player['team']

        file_name = f"{first}_{last}_{pid}_{team}_html.txt"

        # 2) skip anyone not in the pending list
        if file_name not in pending_files:
            print(f"✅ Skipping {file_name} (not pending)")
            continue

        print(f"\n🔄 Row {idx}: {first} {last} ({team} – {pos}); processing {file_name}")

        prompt = (
            PROMPT_TEMPLATE
            .replace('[FIRST]', first)
            .replace('[LAST]', last)
            .replace('[TEAM]', team)
            .replace('[POSITION]', pos)
        )

        if idx == 1 and config.get('debug_prompt', False):
            print("🛑 DEBUG prompt:\n" + prompt)
            pdb.set_trace()

        execute_macro('PromptMaster', file_name=file_name, prompt_text=prompt)
        save_player_html(file_name)

        delay = config.get('delay_between', 2)
        print(f"⏱ Waiting {delay}s before next…")
        time.sleep(delay)

    print("\n🚀 Pending processing complete!")

if __name__ == '__main__':
    # 1) refresh your pending-files list
    check_download_status.main()

    # 2) then hand off control to the shift scheduler, which will
    #    repeatedly invoke your main() loop under your 9h/1h-lunch policy
    run_with_shift(main)