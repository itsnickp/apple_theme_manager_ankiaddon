from __future__ import annotations

from aqt import mw
from aqt.qt import QAction, qconnect

from .dialog import ThemeManagerDialog


_dialog = None


def show_theme_manager():
    global _dialog
    _dialog = ThemeManagerDialog(mw)
    _dialog.show()
    _dialog.raise_()
    _dialog.activateWindow()


def init_addon():
    action = QAction("Apple-Style Theme Manager", mw)
    qconnect(action.triggered, show_theme_manager)
    mw.form.menuTools.addSeparator()
    mw.form.menuTools.addAction(action)
