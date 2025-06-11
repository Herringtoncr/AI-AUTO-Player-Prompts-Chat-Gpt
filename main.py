import os
import csv
import time
import pdb
import pyperclip

from automation.config_loader import config  # loads settings from config/config.yaml
from automation.macro_runner import execute_macro

# Determine CSV path (overrideable via config.yaml)
CSV_REL_PATH = config.get('csv_path', 'csv/players3.csv')
PROJECT_ROOT = os.path.dirname(__file__)
CSV_FILE = os.path.join(PROJECT_ROOT, *CSV_REL_PATH.replace('\\', '/').split('/'))

# Directory to save HTML/snippets (absolute or relative via config.yaml 'output_folder')
user_folder = config.get('output_folder', 'txt')
if os.path.isabs(user_folder):
    SAVE_DIR = user_folder
else:
    SAVE_DIR = os.path.join(PROJECT_ROOT, user_folder)
# ensure the folder exists
os.makedirs(SAVE_DIR, exist_ok=True)

# Prompt template (overrideable via config.yaml under 'prompt_template')
PROMPT_TEMPLATE = config.get('prompt_template', '''
You are a CFB beat writer
TASK: Produce an ultra-condensed NCAAF résumé for [FIRST] [LAST] – [TEAM] [POSITION].

RULES
Use tight bullet points (one line each).

Start every line with either
• an exact date in M-D-YY: format (e.g., 4-26-22:) or
• a season tag using the last two digits (e.g., 22:).

Include only high-value facts:
• recruiting rank / commit year
• starting / bench status & number of starts
• major injuries & return dates
• transfer-portal moves (destination and documented reason — include a source link)
• awards (MVP, All-Conference, etc.)
• current roster / depth-chart status & outlook
• practice-reps status (first-team or second-team) from current-year spring/fall workouts

No fluff, adjectives, or analysis — just facts.

Append a supporting article link at the end of each bullet (in parentheses).

Keep every bullet ≤ 25 words.

Finish with four bullets (same one-line style):
• [POS] room: – snapshot of immediate competition (QB, WR, RB, OL, DL, LB, DB)
• 2025 outlook: – one-line odds of starting or role expectation
• Practice reps: – specify “mostly 1st-team” or “mostly 2nd-team” with source link
• Eligibility: – years remaining (e.g., “3 seasons left through 2027”)

Summary (≤ 45 words):
• Begin with YL X (years of eligibility left)
• Use 2-digit years (e.g., 25, 24) and common team abbreviations (BAMA, PITT, UW, etc.)
• Retain star-rating format (e.g., 4⭐)
• State current-year practice status (1st-team or 2nd-team)
• Cite clear, sourced reason for any portal move (no hearsay)
• No links in the Summary

Excel single-cell format
After the résumé, create a second block titled No-link Excel format (single-cell, pipe-delimited):

NEW: Begin the string with the player’s full name (“First Last”) followed by a pipe (|).

Concatenate every bullet and the Summary in original order, without links, replacing line breaks with |.

Keep pipes (|) only as separators; no extra spaces at either end.

Ensure the entire string fits in one spreadsheet cell.
''')


def read_players(csv_path):
    """Yield a dict for each player: id, first, last, position, team."""
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
    """Retrieve clipboard content and save to SAVE_DIR/file_name."""
    copied_text = pyperclip.paste()
    if not copied_text.strip():
        print(f"❌ Clipboard empty—skipping save for {file_name}")
        return
    saved_file_path = os.path.join(SAVE_DIR, file_name)
    with open(saved_file_path, 'w', encoding='utf-8') as f:
        f.write(copied_text)
    print(f"✅ Content saved to {saved_file_path}")


def main():
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV not found: {CSV_FILE}")
        return

    for idx, player in enumerate(read_players(CSV_FILE), start=1):
        first = player['first']
        last = player['last']
        pid = player['id']
        pos = player['position']
        team = player['team']

        # Construct filename
        file_name = f"{first}_{last}_{pid}_{team}_html.txt"
        print(f"\n🔄 Row {idx}: {first} {last} ({team} – {pos}); will save as {file_name}")

        # Build prompt
        prompt = (
            PROMPT_TEMPLATE
            .replace('[FIRST]', first)
            .replace('[LAST]', last)
            .replace('[TEAM]', team)
            .replace('[POSITION]', pos)
        )

        # Debug prompt if enabled
        if idx == 1 and config.get('debug_prompt', False):
            print("🛑 DEBUG prompt:\n" + prompt)
            pdb.set_trace()

        # Execute the macro
        execute_macro('PromptMaster', file_name=file_name, prompt_text=prompt)

        # Save HTML/snippet from clipboard
        save_player_html(file_name)

        # Pause
        delay = config.get('delay_between', 2)
        print(f"⏱ Waiting {delay}s before next…")
        time.sleep(delay)

    print("\n🚀 All rows processed!")


if __name__ == '__main__':
    main()
