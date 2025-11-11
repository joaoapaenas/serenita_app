# app/core/theme_manager.py
import logging
import os

from PySide6.QtWidgets import QApplication

log = logging.getLogger(__name__)


def apply_theme(app: QApplication, theme_name: str):
    """Loads and applies a QSS stylesheet for the given theme."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    theme_filename = f"style_{theme_name.lower()}.qss"
    style_path = os.path.join(base_path, "..", "assets", "styles", theme_filename)

    try:
        with open(style_path, "r", encoding="utf-8") as f:
            style = f.read()
            app.setStyleSheet(style)
            log.info(f"Successfully loaded '{theme_name}' theme from {theme_filename}.")
    except FileNotFoundError:
        log.warning(f"Stylesheet for theme '{theme_name}' not found at {style_path}. Application may appear unstyled.")