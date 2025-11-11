# app/features/main_window/tutor_runner.py
import logging

from PySide6.QtCore import QObject, Signal, QRunnable

from app.core.tutor_engine.tutor import Tutor
from app.services.interfaces import ICycleSubjectService

log = logging.getLogger(__name__)


class TutorRunner(QRunnable):
    class Signals(QObject):
        finished = Signal(dict)
        error = Signal(str)

    def __init__(self, cycle_config: dict, cycle_subject_service: ICycleSubjectService):
        super().__init__()
        self.signals = self.Signals()
        self.cycle_config = cycle_config
        self.cycle_subject_service = cycle_subject_service

    def run(self):
        log.debug("TutorRunner started in background thread.")
        try:
            tutor = Tutor(self.cycle_subject_service)
            result = tutor.create_study_cycle(self.cycle_config)
            self.signals.finished.emit(result)
        except Exception as e:
            log.error("Error running Tutor engine in background", exc_info=True)
            self.signals.error.emit(f"An unexpected error occurred in the planning engine:\n\n{e}")
        log.debug("TutorRunner finished.")