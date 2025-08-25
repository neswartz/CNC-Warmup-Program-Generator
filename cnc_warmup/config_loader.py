import json
import os
from typing import Any, Dict, Optional

def default_config_path() -> str:
    root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(root, "config", "warmup_config.json")

def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    cfg_path = path or default_config_path()
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_machines(config: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    machines = config.get("machines", {})
    return {
        str(k): {
            "x_travel": str(v.get("x_travel", 300)),
            "y_travel": str(v.get("y_travel", 300)),
            "z_travel": str(v.get("z_travel", 300)),
        }
        for k, v in machines.items()
    }

def get_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config.get("defaults", {}))


