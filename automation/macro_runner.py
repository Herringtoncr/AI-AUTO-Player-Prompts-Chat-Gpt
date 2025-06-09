import pyautogui
import time
from automation.config_loader import config

def execute_macro(macro_name, file_name=None):  # Add 'file_name' as an optional argument
    """ Executes macro actions step-by-step """
    macro = config["macros"].get(macro_name, {})

    if not macro:
        print(f"❌ Macro '{macro_name}' not found!")
        return

    for action in macro.get("actions", []):
        if "wait" in action:
            print(f"⏳ Waiting for {action['wait']} seconds...")
            time.sleep(action["wait"])  # Log and add structured wait times
        elif "press_key" in action:
            keys = action["press_key"].split("+")
            pyautogui.hotkey(*keys)
            time.sleep(1)  # Small pause after key commands
        elif "mouse_click" in action:
            click_data = action["mouse_click"]
            pyautogui.click(x=click_data["x"], y=click_data["y"])
            time.sleep(1)  # Ensure click is registered before moving on

    print(f"✅ Executed macro: {macro_name}")