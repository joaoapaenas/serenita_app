# app/core/logger.py

import logging
import logging.handlers
import os
import sys

# Try to import coloredlogs, but fall back gracefully if it's not installed
try:
    import coloredlogs

    HAS_COLOREDLOGS = True
except ImportError:
    HAS_COLOREDLOGS = False

# Define the path for the log file, placing it in the user's home directory
# This is a robust location that avoids permission issues.
LOG_DIR = os.path.join(os.path.expanduser("~"), ".serenita")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "serenita_app.log")


def setup_logging():
    """
    Configures the root logger for the entire application.
    This should be called once at application startup.
    """
    # Create a logger instance
    log = logging.getLogger()  # Get the root logger
    log.setLevel(logging.DEBUG)  # Set the lowest level to capture all messages

    # --- 1. File Handler ---
    # This handler writes logs to a file and rotates it when it gets too big.
    # Max size: 5MB, keep 5 backup files.
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)  # Only write INFO and above to the file
    log.addHandler(file_handler)

    # --- 2. Console Handler (with colors if available) ---
    # This handler prints logs to the console (stderr).
    console_handler = logging.StreamHandler(sys.stdout)

    if HAS_COLOREDLOGS:
        # Use coloredlogs for a nice, readable console output
        console_formatter = coloredlogs.ColoredFormatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        # coloredlogs handles its own level coloring
    else:
        # Use a standard formatter if coloredlogs is not available
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

    console_handler.setLevel(logging.DEBUG)  # Show all messages in the console during dev
    log.addHandler(console_handler)

    print(f"Logging configured. Log file at: {LOG_FILE_PATH}")
