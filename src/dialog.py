from __future__ import annotations

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    Qt,
)

from .backup import latest_backup_for_model
from .installer import apply_preset_to_model, restore_model_from_latest_backup
from .matcher import detect_preset_key, field_names_for_model
from .presets import PRESETS, preset_options


try:
    USER_ROLE = Qt.ItemDataRole.UserRole
except AttributeError:
    USER_ROLE = Qt.UserRole


def _yes_button():
    try:
        return QMessageBox.StandardButton.Yes
    except AttributeError:
        return QMessageBox.Yes


def _no_button():
    try:
        return QMessageBox.StandardButton.No
    except AttributeError:
        return QMessageBox.No


def _question(parent, title, text):
    result = QMessageBox.question(parent, title, text, _yes_button() | _no_button())
    return result == _yes_button()


class ThemeManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Apple-Style Theme Manager")
        self.resize(920, 620)

        self.model_list = QListWidget()
        self.model_list.currentItemChanged.connect(self.on_model_changed)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Auto-detect from fields", "auto")
        for preset in preset_options():
            self.preset_combo.addItem(preset.label, preset.key)

        self.apply_all_templates = QCheckBox("Apply to all card templates in this note type")
        self.apply_all_templates.setChecked(False)

        self.details = QTextEdit()
        self.details.setReadOnly(True)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_models)

        self.detect_button = QPushButton("Detect Preset")
        self.detect_button.clicked.connect(self.detect_selected)

        self.apply_button = QPushButton("Apply Theme")
        self.apply_button.clicked.connect(self.apply_theme)

        self.restore_button = QPushButton("Restore Latest Backup")
        self.restore_button.clicked.connect(self.restore_backup)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        left = QVBoxLayout()
        left.addWidget(QLabel("Note types"))
        left.addWidget(self.model_list)
        left.addWidget(self.refresh_button)

        controls = QVBoxLayout()
        controls.addWidget(QLabel("Preset"))
        controls.addWidget(self.preset_combo)
        controls.addWidget(self.apply_all_templates)
        controls.addWidget(self.detect_button)
        controls.addWidget(self.apply_button)
        controls.addWidget(self.restore_button)
        controls.addStretch(1)
        controls.addWidget(self.close_button)

        right = QVBoxLayout()
        right.addWidget(QLabel("Inspection / dry run"))
        right.addWidget(self.details)

        main = QHBoxLayout()
        main.addLayout(left, 3)
        main.addLayout(controls, 2)
        main.addLayout(right, 4)
        self.setLayout(main)

        self.refresh_models()

    def note_count(self, model):
        try:
            return mw.col.db.scalar("select count() from notes where mid = ?", model["id"]) or 0
        except Exception:
            return 0

    def refresh_models(self):
        self.model_list.clear()
        models = sorted(mw.col.models.all(), key=lambda m: m.get("name", "").lower())

        for model in models:
            count = self.note_count(model)
            item = QListWidgetItem(f"{model.get('name')} [{count} notes]")
            item.setData(USER_ROLE, model.get("id"))
            self.model_list.addItem(item)

        if self.model_list.count():
            self.model_list.setCurrentRow(0)

    def selected_model(self):
        item = self.model_list.currentItem()
        if not item:
            return None
        model_id = item.data(USER_ROLE)
        return mw.col.models.get(model_id)

    def selected_preset_key(self):
        key = self.preset_combo.currentData()
        if key == "auto":
            model = self.selected_model()
            if model is None:
                return None
            return detect_preset_key(field_names_for_model(model))
        return key

    def on_model_changed(self):
        model = self.selected_model()
        if model is None:
            self.details.setPlainText("No note type selected.")
            return

        fields = sorted(field_names_for_model(model))
        detected = detect_preset_key(fields)
        backup = latest_backup_for_model(model.get("id"))

        text = [
            f"Note type: {model.get('name')}",
            f"Model ID: {model.get('id')}",
            f"Card templates: {len(model.get('tmpls', []))}",
            "",
            "Fields:",
            *[f"  - {field}" for field in fields],
            "",
            f"Detected preset: {PRESETS[detected].label if detected else 'None'}",
            f"Latest backup: {backup.name if backup else 'None'}",
        ]

        if detected and PRESETS[detected].warning:
            text.extend(["", "Warning:", PRESETS[detected].warning])

        self.details.setPlainText("\n".join(text))

    def detect_selected(self):
        model = self.selected_model()
        if model is None:
            return

        detected = detect_preset_key(field_names_for_model(model))
        if not detected:
            QMessageBox.warning(
                self,
                "No preset detected",
                "No matching preset was found for this note type. Check the field names.",
            )
            return

        for index in range(self.preset_combo.count()):
            if self.preset_combo.itemData(index) == detected:
                self.preset_combo.setCurrentIndex(index)
                break

        self.on_model_changed()

    def apply_theme(self):
        model = self.selected_model()
        if model is None:
            return

        preset_key = self.selected_preset_key()
        if not preset_key:
            QMessageBox.warning(
                self,
                "No preset",
                "No preset was selected or detected for this note type.",
            )
            return

        preset = PRESETS[preset_key]
        warning = f"Apply preset:\n\n{preset.label}\n\nTo note type:\n{model.get('name')}\n\nA backup will be created first."
        if preset.warning:
            warning += f"\n\nWarning: {preset.warning}"

        if not _question(self, "Apply theme?", warning):
            return

        try:
            changed = apply_preset_to_model(
                model,
                preset_key,
                apply_to_all_templates=self.apply_all_templates.isChecked(),
                auto_backup=True,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Apply failed", str(exc))
            return

        QMessageBox.information(
            self,
            "Theme applied",
            f"Theme applied to {changed} card template(s). Sync to AnkiWeb, then sync AnkiDroid.",
        )
        self.on_model_changed()

    def restore_backup(self):
        model = self.selected_model()
        if model is None:
            return

        if not _question(
            self,
            "Restore latest backup?",
            f"Restore the latest backup for:\n\n{model.get('name')}\n\nCurrent templates and CSS will be overwritten.",
        ):
            return

        try:
            path = restore_model_from_latest_backup(model)
        except Exception as exc:
            QMessageBox.critical(self, "Restore failed", str(exc))
            return

        QMessageBox.information(self, "Restored", f"Restored backup:\n{path.name}")
        self.on_model_changed()
