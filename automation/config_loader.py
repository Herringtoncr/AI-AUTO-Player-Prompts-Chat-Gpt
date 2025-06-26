import os
import yaml

def load_config():
    # 1. Build an absolute path to config/config.yaml (so it works no matter what cwd is)
    base_dir = os.path.dirname(__file__)           # .../your-repo/automation
    cfg_path = os.path.join(base_dir, os.pardir,   # go up to repo root
                            "config", "config.yaml")

    # 2. Open the file in UTF-8, ignoring undecodable bytes
    with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
        data = yaml.safe_load(f)

    return data

# 3. Load once at import time
config = load_config()
