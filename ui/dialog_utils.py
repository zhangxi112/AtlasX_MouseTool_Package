"""Dialog helpers for readable themed QMessageBox and QColorDialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QColorDialog, QMessageBox, QWidget


def _dialog_colors(mode: str) -> dict[str, str]:
    dark = mode != "light"
    if dark:
        return {
            "window": "#0F172A",
            "panel": "#111C2E",
            "panel_soft": "#18263D",
            "text": "#F8FAFC",
            "muted": "#CBD5E1",
            "accent": "#22D3EE",
            "accent_soft": "rgba(34, 211, 238, 0.18)",
            "border": "rgba(148, 163, 184, 0.28)",
            "input": "#0B1322",
            "selection": "rgba(34, 211, 238, 0.26)",
            "button_text": "#F8FAFC",
        }
    return {
        "window": "#F5F9FF",
        "panel": "#FFFFFF",
        "panel_soft": "#EEF5FF",
        "text": "#0F172A",
        "muted": "#334155",
        "accent": "#0284C7",
        "accent_soft": "rgba(2, 132, 199, 0.16)",
        "border": "rgba(15, 23, 42, 0.18)",
        "input": "#FFFFFF",
        "selection": "rgba(2, 132, 199, 0.18)",
        "button_text": "#0F172A",
    }


def build_dialog_stylesheet(mode: str) -> str:
    colors = _dialog_colors(mode)
    return f"""
    QDialog, QMessageBox, QColorDialog {{
        background: {colors['window']};
        color: {colors['text']};
    }}
    QMessageBox QLabel, QColorDialog QLabel {{
        color: {colors['text']};
        background: transparent;
        font-size: 13px;
    }}
    QMessageBox QPushButton, QColorDialog QPushButton {{
        min-width: 104px;
        min-height: 38px;
        padding: 8px 16px;
        border-radius: 14px;
        border: 1px solid {colors['border']};
        background: {colors['panel_soft']};
        color: {colors['button_text']};
        font-weight: 600;
    }}
    QMessageBox QPushButton:hover, QColorDialog QPushButton:hover {{
        border-color: {colors['accent']};
        background: {colors['accent_soft']};
        color: {colors['text']};
    }}
    QMessageBox QPushButton:pressed, QColorDialog QPushButton:pressed {{
        background: {colors['selection']};
    }}
    QMessageBox QFrame, QColorDialog QFrame {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 14px;
    }}
    QColorDialog QLineEdit, QColorDialog QSpinBox {{
        background: {colors['input']};
        color: {colors['text']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 8px 10px;
        selection-background-color: {colors['selection']};
    }}
    QColorDialog QAbstractSpinBox::up-button, QColorDialog QAbstractSpinBox::down-button {{
        width: 20px;
        border: none;
        background: {colors['panel_soft']};
    }}
    QColorDialog QAbstractSpinBox::up-button:hover, QColorDialog QAbstractSpinBox::down-button:hover {{
        background: {colors['accent_soft']};
    }}
    QColorDialog QWellArray QPushButton {{
        min-width: 22px;
        min-height: 22px;
        padding: 0;
        border-radius: 6px;
    }}
    """


def build_dialog_palette(mode: str) -> QPalette:
    colors = _dialog_colors(mode)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors['window']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text']))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors['input']))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['panel']))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['panel']))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['text']))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors['text']))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors['panel_soft']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['button_text']))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['accent']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF" if mode != 'light' else '#0F172A'))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors['muted']))
    return palette


def apply_dialog_theme(widget: QWidget, mode: str) -> None:
    widget.setPalette(build_dialog_palette(mode))
    widget.setStyleSheet(build_dialog_stylesheet(mode))


def show_themed_message(parent: QWidget | None, mode: str, title: str, text: str, icon: QMessageBox.Icon) -> QMessageBox.StandardButton:
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    dialog.setIcon(icon)
    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    apply_dialog_theme(dialog, mode)
    dialog.exec()
    return dialog.standardButton(dialog.clickedButton()) if dialog.clickedButton() is not None else QMessageBox.StandardButton.Ok


def show_information(parent: QWidget | None, mode: str, title: str, text: str) -> QMessageBox.StandardButton:
    return show_themed_message(parent, mode, title, text, QMessageBox.Icon.Information)


def show_warning(parent: QWidget | None, mode: str, title: str, text: str) -> QMessageBox.StandardButton:
    return show_themed_message(parent, mode, title, text, QMessageBox.Icon.Warning)


def show_critical(parent: QWidget | None, mode: str, title: str, text: str) -> QMessageBox.StandardButton:
    return show_themed_message(parent, mode, title, text, QMessageBox.Icon.Critical)


def pick_color(parent: QWidget | None, mode: str, current_value: str, title: str) -> QColor:
    dialog = QColorDialog(QColor(current_value), parent)
    dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
    dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
    dialog.setWindowTitle(title)
    apply_dialog_theme(dialog, mode)
    if dialog.exec() != QColorDialog.DialogCode.Accepted:
        return QColor()
    return dialog.selectedColor()


def show_question(parent: QWidget | None, mode: str, title: str, text: str) -> bool:
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    dialog.setDefaultButton(QMessageBox.StandardButton.No)
    dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    apply_dialog_theme(dialog, mode)
    result = dialog.exec()
    return result == int(QMessageBox.StandardButton.Yes)
