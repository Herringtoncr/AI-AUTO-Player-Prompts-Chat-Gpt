import os
import csv
import time
import pdb

from automation.config_loader import config  # loads settings from config/config.yaml
from automation.macro_runner    import execute_macro

# Determine CSV path (overrideable via config.yaml)
CSV_REL_PATH = config.get('csv_path', 'csv/players2.csv')
PROJECT_ROOT = os.path.dirname(__file__)
CSV_FILE = os.path.join(PROJECT_ROOT, *CSV_REL_PATH.replace('\\', '/').split('/'))

# Prompt template (overrideable via config.yaml under 'prompt_template')
PROMPT_TEMPLATE = config.get('prompt_template', '''
    You are a CFB beat writer.
    TASK: Produce an ultra-condensed NCAAF résumé for [Player Name] [Position].

    RULES

    Use tight bullet points (one line each).

    Begin every line with an exact date or season tag (e.g., 2022: or 26 Apr 2023:).

    Include only high-value facts:
    • recruiting rank/commit year
    • starting/bench status & number of starts
    • major injuries & return dates
    • transfer-portal moves (destination & reason if clear)
    • awards (MVP, All-Conference, etc.)
    • current roster/depth-chart status & outlook

    No fluff, adjectives, or analysis—just facts.

    Append an article link to support each bullet (in parentheses).

    Keep every bullet ≤ 25 words.

    7. End with four bullets: 
• WR room: – snapshot of immediate competition 
• 2025 outlook: – one-line odds of starting or role expectation 
• Practice reps: – specify “mostly 1st-team” or “mostly 2nd-team” with source link 
• Year of eligibility left
8. Finish with a one-sentence *Summary:* (≤ 45 words) that highlights the career arc *and notes first/second-team practice status*.
''')


def read_players(csv_path):
    """Yield (player_name, position) from the CSV."""
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name     = row.get('Player Name', '').strip()
            position = row.get('Position', '').strip()
            if not name or not position:
                continue
            yield name, position


def main():
    # Ensure CSV exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV not found: {CSV_FILE}")
        return

    for idx, (player_name, position) in enumerate(read_players(CSV_FILE), start=1):
        print(f"\n🔄 Row {idx}: {player_name} ({position})")

        # Build the prompt text by injecting CSV values
        prompt = PROMPT_TEMPLATE.replace('[Player Name]', player_name).replace('[Position]', position)

        # DEBUG: break into pdb on first row to inspect prompt
        if idx == 1:
            print("🛑 DEBUG - first constructed prompt:")
            print(prompt)
            pdb.set_trace()

        # Execute macro, passing in prompt_text for any '{{prompt}}' write steps
        execute_macro('PromptMaster', file_name=player_name, prompt_text=prompt)

        # Delay between rows
        delay = config.get('delay_between', 2)
        print(f"⏱ Waiting {delay}s before next…")
        time.sleep(delay)

    print("\n🚀 All rows processed!")


if __name__ == '__main__':
    main()
