import os
import yaml

def load_config():
    # build path to config/config.yaml relative to this file
    base_dir = os.path.dirname(__file__)                # .../automation
    cfg_path = os.path.join(base_dir, "..", "config", "config.yaml")
    # open with UTF-8 (use "utf-8-sig" if you may have a BOM)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()
print("Loaded Macros:", config["macros"])