import pyautogui
import time
from automation.config_loader import config

# Map generic key names to PyAutoGUI-recognized names
KEY_MAP = {
    "win": "winleft",  # use Windows key (left)
    "ctrl": "ctrl",
    "shift": "shift",
}

def execute_macro(macro_name, file_name=None):
    """Executes a named macro from config, with detailed logging, focus delay, and fallbacks."""
    macros = config.get("macros", {})
    print(f"🔧 Loaded Macros: {list(macros.keys())}")
    print(f"🔧 Executing macro '{macro_name}' (file_name={file_name})")

    macro = macros.get(macro_name)
    if not macro:
        print(f"❌ Macro '{macro_name}' not found in config!")
        return

    # Optional initial wait to give focus to the target application/window
    initial_wait = config.get("initial_wait", 1)
    if initial_wait > 0:
        print(f"⏳ Initial wait for {initial_wait}s to set focus...")
        time.sleep(initial_wait)

    for action in macro.get("actions", []):
        if "wait" in action:
            secs = action["wait"]
            print(f"⏳ Waiting for {secs}s...")
            time.sleep(secs)

        elif "press_key" in action:
            combo = action["press_key"].split("+")
            # Normalize and map each key
            keys = [KEY_MAP.get(k.lower(), k.lower()) for k in combo]
            print(f"⌨️ Pressing: {' + '.join(keys)}")
            try:
                pyautogui.hotkey(*keys)
            except Exception as e:
                print(f"⚠️ hotkey failed ({e}), using fallback keyDown/press/keyUp")
                pyautogui.keyDown(keys[0])
                for k in keys[1:]:
                    pyautogui.press(k)
                pyautogui.keyUp(keys[0])
            time.sleep(config.get("post_key_delay", 0.5))

        elif "mouse_click" in action:
            click = action["mouse_click"]
            x, y = click.get("x"), click.get("y")
            print(f"🖱 Clicking at coordinates ({x}, {y})")
            pyautogui.click(x=x, y=y)
            time.sleep(config.get("post_click_delay", 0.5))

        else:
            print(f"⚠️ Unknown action type: {action}")

    print(f"✅ Executed macro: {macro_name}")
