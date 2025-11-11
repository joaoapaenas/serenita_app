# app/core/signals.py

from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    """
    A central hub for application-wide signals (Observer pattern).
    This allows for decoupled communication between different parts of the app.
    """
    # Emitted whenever cycle or subject configuration changes,
    # requiring a refresh of the main dashboard and lists.
    data_changed = Signal()

    # Emitted when the application theme (stylesheet) is changed.
    theme_changed = Signal()


# Create a single, globally accessible instance.
app_signals = AppSignals()