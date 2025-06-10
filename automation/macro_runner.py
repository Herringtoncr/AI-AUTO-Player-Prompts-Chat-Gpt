import pyautogui
import pyclip
import time
from automation.config_loader import config

# Map generic key names to PyAutoGUI-recognized names
KEY_MAP = {
    "win": "winleft",
    "ctrl": "ctrl",
    "shift": "shift",
    "alt": "alt",
}


def execute_macro(macro_name, file_name=None, prompt_text=None):
    """Executes a named macro from config, with optional typed prompt_text and clipboard actions."""
    macros = config.get("macros", {})
    print(f"🔧 Loaded macros: {list(macros.keys())}")
    print(f"🔧 Executing macro '{macro_name}' (file_name={file_name})")

    macro = macros.get(macro_name)
    if not macro:
        print(f"❌ Macro '{macro_name}' not found in config!")
        return

    # Initial focus delay
    initial_wait = config.get("initial_wait", 1)
    if initial_wait > 0:
        print(f"⏳ Initial wait for {initial_wait}s")
        time.sleep(initial_wait)

    for action in macro.get("actions", []):
        if "wait" in action:
            secs = action["wait"]
            print(f"⏳ Waiting for {secs}s")
            time.sleep(secs)

        elif "press_key" in action:
            combo = action["press_key"].split("+")
            keys = [KEY_MAP.get(k.lower(), k.lower()) for k in combo]
            print(f"⌨️ Pressing: {' + '.join(keys)}")
            try:
                pyautogui.hotkey(*keys)
            except Exception as e:
                print(f"⚠️ hotkey failed ({e}), falling back")
                pyautogui.keyDown(keys[0])
                for k in keys[1:]: pyautogui.press(k)
                pyautogui.keyUp(keys[0])
            time.sleep(config.get("post_key_delay", config.get("DEFAULT_DELAY", 0.5)))

        elif "pyclip" in action:
            raw = action.get("pyclip", "")
            text = raw.replace("{{prompt}}", prompt_text or "")
            print(f"📋 Copying to clipboard: {text[:30]}…")
            try:
                pyclip.copy(text)
            except Exception as e:
                print(f"⚠️ pyclip.copy failed: {e}")
            time.sleep(config.get("post_clip_delay", config.get("DEFAULT_DELAY", 0.5)))

        elif "write" in action:
            raw = action.get("write", "")
            text = raw.replace("{{prompt}}", prompt_text or "")
            interval = config.get("typing_interval", 0.05)
            print(f"✍️ Writing text (interval={interval}s)...")
            pyautogui.write(text, interval=interval)
            time.sleep(config.get("post_key_delay", config.get("DEFAULT_DELAY", 0.5)))

        elif "mouse_click" in action:
            click = action["mouse_click"]
            x, y = click.get("x"), click.get("y")
            print(f"🖱 Clicking at ({x}, {y})")
            pyautogui.click(x=x, y=y)
            time.sleep(config.get("post_click_delay", config.get("DEFAULT_DELAY", 0.5)))

        else:
            print(f"⚠️ Unknown action: {action}")

    print(f"✅ Executed macro: {macro_name}")
