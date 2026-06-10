from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import List, Optional

from aqt import mw


ADDON_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ADDON_ROOT / "user_files" / "backups"


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")
    return cleaned[:80] or "model"


def backup_model(model, reason: str = "manual") -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "addon": "apple_theme_manager",
        "reason": reason,
        "timestamp": int(time.time()),
        "model_id": model.get("id"),
        "model_name": model.get("name"),
        "css": model.get("css", ""),
        "templates": [
            {
                "name": template.get("name", ""),
                "qfmt": template.get("qfmt", ""),
                "afmt": template.get("afmt", ""),
            }
            for template in model.get("tmpls", [])
        ],
    }

    stamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}_{model.get('id')}_{_safe_name(model.get('name', 'model'))}.json"
    path = BACKUP_DIR / filename
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def backup_files_for_model(model_id) -> List[Path]:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for path in BACKUP_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if str(data.get("model_id")) == str(model_id):
            files.append(path)

    return sorted(files, key=lambda p: p.name, reverse=True)


def latest_backup_for_model(model_id) -> Optional[Path]:
    files = backup_files_for_model(model_id)
    return files[0] if files else None


def load_backup(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def restore_latest_backup(model) -> Path:
    path = latest_backup_for_model(model.get("id"))
    if path is None:
        raise FileNotFoundError("No backup exists for this note type.")

    data = load_backup(path)
    model["css"] = data.get("css", "")

    old_templates = data.get("templates", [])
    for index, old_template in enumerate(old_templates):
        if index >= len(model.get("tmpls", [])):
            break
        model["tmpls"][index]["qfmt"] = old_template.get("qfmt", "")
        model["tmpls"][index]["afmt"] = old_template.get("afmt", "")

    return path
