# app/core/icon_manager.py
import logging

import qtawesome as qta
from PySide6.QtGui import QIcon

log = logging.getLogger(__name__)

# Define theme colors for easy access
THEME_TEXT_COLOR = "#EAEAEA"
THEME_ACCENT_COLOR = "#FFCC00"
THEME_ACCENT_TEXT_COLOR = "#111111"

# Icon Map with the new icon added
ICON_MAP = {
    # General Actions
    "PLUS": "fa6s.plus",
    "PLUS_CIRCLE": "fa6s.circle-plus",
    "EDIT": "fa6s.pencil",
    "DELETE": "fa6s.trash-can",
    "SAVE": "fa6s.floppy-disk",
    "CANCEL": "fa6s.xmark",
    "CONFIGURATIONS": "fa6s.gear",
    "ADD": "fa6s.plus",
    "NEW_CYCLE": "fa6s.file-circle-plus",
    "QUIT": "fa6s.arrow-right-from-bracket",
    "UNDO": "fa6s.rotate-left",
    "REDO": "fa6s.rotate-right",
    "HELP": "fa6s.circle-question",
    "ARROW_RIGHT": "fa6s.arrow-right",
    "ARROW_LEFT": "fa6s.arrow-left",
    "MAGIC_WAND": "fa6s.wand-magic-sparkles",

    "PAUSE": "fa6s.pause",
    "FINISH_FLAG": "fa6s.flag-checkered",

    # Status & Navigation
    "ACTIVE_STATUS": "fa6s.star",
    "OVERVIEW": "fa6s.house",
    "HISTORY": "fa6s.clock-rotate-left",
    "SUBJECTS": "fa6s.book",
    "SUBJECT": "fa6s.bookmark",
    "MINIMIZE": "fa6s.window-minimize",
    "DRAG_HANDLE": "fa6s.grip-vertical",
    # Dashboard Actions
    "START_SESSION": "fa6s.play",
    "VIEW_PERFORMANCE": "fa6s.chart-line",
    "REBALANCE": "fa6s.scale-balanced",

    # Rebalancer
    "ACCEPT": "fa6s.check",
}


def get_icon(name: str, color: str = THEME_TEXT_COLOR) -> QIcon:
    """Gets a QIcon from the icon map using qtawesome."""
    if name not in ICON_MAP:
        log.warning(f"Icon name '{name}' not found in ICON_MAP. Using fallback.")
        # FIX: The correct icon name is 'fa6s.circle-question' for FontAwesome 6 Solid
        return qta.icon("fa6s.circle-question", color="red")

    icon_name = ICON_MAP[name]
    return qta.icon(icon_name, color=color)