from __future__ import annotations

from typing import Iterable, Optional, Set

from .presets import PRESETS


def field_names_for_model(model) -> Set[str]:
    return {field.get("name", "") for field in model.get("flds", [])}


def detect_preset_key(field_names: Iterable[str]) -> Optional[str]:
    fields = set(field_names)

    ordered_keys = [
        "image_occlusion",
        "cloze_content",
        "basic_additional",
        "basic_code",
        "expression",
        "code_output",
        "code_howto",
        "code_refactor",
        "interactive_coding",
        "cloze_text",
        "code_output_question",
        "basic",
    ]

    for key in ordered_keys:
        preset = PRESETS[key]
        if preset.required_fields.issubset(fields):
            return key

    return None


def missing_fields(model, preset_key: str):
    fields = field_names_for_model(model)
    required = PRESETS[preset_key].required_fields
    return sorted(required - fields)
