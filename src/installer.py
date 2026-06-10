from __future__ import annotations

from aqt import mw

from .backup import backup_model, restore_latest_backup
from .matcher import missing_fields
from .presets import load_preset


def save_model(model):
    manager = mw.col.models

    if hasattr(manager, "save"):
        try:
            manager.save(model)
            return
        except TypeError:
            manager.save(model, templates=True)
            return

    if hasattr(manager, "update_dict"):
        manager.update_dict(model)
        return

    if hasattr(manager, "flush"):
        manager.flush(model)
        return

    raise RuntimeError("Unsupported Anki model manager: could not save note type.")


def apply_preset_to_model(
    model,
    preset_key: str,
    *,
    apply_to_all_templates: bool = False,
    auto_backup: bool = True,
):
    missing = missing_fields(model, preset_key)
    if missing:
        raise ValueError(
            "This preset cannot be applied because the note type is missing fields: "
            + ", ".join(missing)
        )

    if auto_backup:
        backup_model(model, reason=f"before_apply_{preset_key}")

    loaded = load_preset(preset_key)
    front = loaded["front"]
    back = loaded["back"]
    css = loaded["css"]

    templates = model.get("tmpls", [])
    if not templates:
        raise ValueError("This note type has no card templates.")

    targets = templates if apply_to_all_templates else templates[:1]

    for template in targets:
        template["qfmt"] = front
        template["afmt"] = back

    model["css"] = css
    save_model(model)
    mw.reset()
    return len(targets)


def restore_model_from_latest_backup(model):
    path = restore_latest_backup(model)
    save_model(model)
    mw.reset()
    return path
