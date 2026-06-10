from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Dict


ADDON_ROOT = Path(__file__).resolve().parents[1]
THEME_DIR = ADDON_ROOT / "themes"


@dataclass(frozen=True)
class Preset:
    key: str
    label: str
    required_fields: FrozenSet[str]
    front_file: str
    back_file: str
    css_file: str = "shared.css"
    warning: str = ""


PRESETS: Dict[str, Preset] = {
    "basic": Preset(
        key="basic",
        label="Basic: Front / Back",
        required_fields=frozenset({"Front", "Back"}),
        front_file="basic_front.html",
        back_file="basic_back.html",
    ),
    "basic_additional": Preset(
        key="basic_additional",
        label="Basic + Additional Info + Options",
        required_fields=frozenset({"Front", "Back", "Additional Info", "With Options"}),
        front_file="basic_additional_front.html",
        back_file="basic_additional_back.html",
    ),
    "basic_code": Preset(
        key="basic_code",
        label="Basic + Back - Basic / Back - Code",
        required_fields=frozenset({"Front", "Back - Basic", "Back - Code"}),
        front_file="basic_code_front.html",
        back_file="basic_code_back.html",
    ),
    "cloze_text": Preset(
        key="cloze_text",
        label="Cloze: Text / Extra / Tags",
        required_fields=frozenset({"Text", "Extra"}),
        front_file="cloze_text_front.html",
        back_file="cloze_text_back.html",
    ),
    "cloze_content": Preset(
        key="cloze_content",
        label="Enhanced Cloze: Content / Note / Mnemonics / Extra / Cloze99",
        required_fields=frozenset({"Content", "Note", "Mnemonics", "Extra", "Cloze99"}),
        front_file="cloze_content_front.html",
        back_file="cloze_content_back.html",
    ),
    "expression": Preset(
        key="expression",
        label="Expression: Expression / Explanation / Equivalent / Comments",
        required_fields=frozenset({"Expression", "Explanation", "Equivalent", "Comments"}),
        front_file="expression_front.html",
        back_file="expression_back.html",
    ),
    "code_output": Preset(
        key="code_output",
        label="Code Output: Code / Output / Explanation / Context",
        required_fields=frozenset({"Code", "Output", "Explanation", "Context"}),
        front_file="code_output_front.html",
        back_file="code_output_back.html",
    ),
    "code_output_question": Preset(
        key="code_output_question",
        label="Code Output Question: Code / Output",
        required_fields=frozenset({"Code", "Output"}),
        front_file="code_output_question_front.html",
        back_file="code_output_question_back.html",
    ),
    "code_howto": Preset(
        key="code_howto",
        label="Code How-To: Effect / How / Comments / Context",
        required_fields=frozenset({"Effect", "How", "Comments", "Context"}),
        front_file="code_howto_front.html",
        back_file="code_howto_back.html",
    ),
    "code_refactor": Preset(
        key="code_refactor",
        label="Code Refactor: Original / Better / Comments / Context",
        required_fields=frozenset({"Original", "Better", "Comments", "Context"}),
        front_file="code_refactor_front.html",
        back_file="code_refactor_back.html",
    ),
    "interactive_coding": Preset(
        key="interactive_coding",
        label="Interactive Coding: Question / Type Hint / Answer",
        required_fields=frozenset({"Question", "Type Hint", "Answer"}),
        front_file="interactive_coding_front.html",
        back_file="interactive_coding_back.html",
    ),
    "cloze_21_v2": Preset(
        key="cloze_21_v2",
        label="Enhanced Cloze 2.1 v2",
        required_fields=frozenset({"Content", "Note", "Mnemonics", "Extra", "Cloze99"}),
        front_file="cloze_content_front.html",
        back_file="cloze_content_back.html",
        css_file="shared.css",
    ),
    "cloze_21_v2plus": Preset(
        key="cloze_21_v2plus",
        label="Enhanced Cloze 2.1 v2+",
        required_fields=frozenset({"Content", "Note", "Mnemonics", "Extra", "Cloze99"}),
        front_file="cloze_content_front.html",
        back_file="cloze_content_back.html",
        css_file="shared.css",
    ),
    "image_occlusion": Preset(
        key="image_occlusion",
        label="Image Occlusion Enhanced: Image / Question Mask / Answer Mask",
        required_fields=frozenset({"Image", "Question Mask", "Answer Mask"}),
        front_file="image_occlusion_front.html",
        back_file="image_occlusion_back.html",
        warning="Image Occlusion cards are fragile. Test on a copied profile before applying broadly.",
    ),
}


def preset_options():
    return list(PRESETS.values())


def read_theme_file(filename: str) -> str:
    path = THEME_DIR / filename
    return path.read_text(encoding="utf-8")


def load_preset(key: str):
    preset = PRESETS[key]
    return {
        "preset": preset,
        "front": read_theme_file(preset.front_file),
        "back": read_theme_file(preset.back_file),
        "css": read_theme_file(preset.css_file),
    }
