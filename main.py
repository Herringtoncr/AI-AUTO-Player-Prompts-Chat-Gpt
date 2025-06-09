import os
import csv
import time
import pyperclip

from automation.config_loader import config  # config.yaml loader
from automation.macro_runner    import execute_macro

# Determine CSV path (overrideable in config.yaml)
CSV_REL_PATH = config.get("csv_path", "csv/players.csv")
PROJECT_ROOT = os.path.dirname(__file__)
CSV_FILE = os.path.join(PROJECT_ROOT, *CSV_REL_PATH.replace("\\", "/").split("/"))


def read_players(csv_path):
    """Yield (player_name, prompt_text, link) from the CSV."""
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name   = row.get('PlayerName', '').strip()
            prompt = row.get('Prompts', '').strip()
            link   = row.get('Links', '').strip()
            if not name or not prompt:
                continue
            yield name, prompt, link


def main():
    # Test: ensure macro works standalone first
    if config.get('test_macro_only', False):
        print("🔧 TEST MODE: Running PromptMaster only")
        time.sleep(config.get('initial_wait', 1))
        execute_macro('PromptMaster')
        return

    # Ensure CSV exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV not found: {CSV_FILE}")
        return

    # Process each CSV row
    for idx, (player_name, prompt_text, link) in enumerate(read_players(CSV_FILE), start=1):
        print(f"\n🔄 Row {idx}: {player_name}")

        # Copy prompt to clipboard (you can embed link or name into prompt_text here)
        pyperclip.copy(prompt_text)
        print(f"📋 Copied prompt: {prompt_text[:60]}…")

        # Execute your macro with optional file_name context
        execute_macro('PromptMaster', file_name=player_name)

        # Delay between each
        delay = config.get('delay_between', 2)
        print(f"⏱ Waiting {delay}s before next…")
        time.sleep(delay)

    print("\n🚀 All rows processed!")


if __name__ == '__main__':
    main()
