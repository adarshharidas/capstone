 
import json
from pathlib import Path
from typing import Any
 
 
def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)
 
 
def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
 
 
def load_dataset(data_dir: Path) -> dict[str, Any]:
    return {
        "incidents": load_json(data_dir / "incidents.json"),
        "builds": load_json(data_dir / "builds.json"),
        "deployments": load_json(data_dir / "deployments.json"),
        "alerts": load_json(data_dir / "alerts.json"),
        "sla_policies": load_json(data_dir / "sla_policies.json"),
    }
 
 
 