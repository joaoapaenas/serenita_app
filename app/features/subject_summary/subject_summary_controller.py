# app/features/subject_summary/subject_summary_controller.py

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget

from app.services.interfaces import IPerformanceService, IMasterSubjectService
from .subject_summary_view import SubjectSummaryView


class SubjectSummaryController(QObject):
    """Controller for the subject summary view."""

    def __init__(self, view: SubjectSummaryView, v20_plan_data: dict,
                 performance_service: IPerformanceService, master_subject_service: IMasterSubjectService,
                 user_id: int, parent: QObject | None = None):
        super().__init__(parent)

        self._view = view
        processed_subjects = v20_plan_data.get('processed_subjects', [])

        # --- Populate Summary Tab ---
        total_time_map = performance_service.get_study_time_summary(user_id, days_ago=9999)
        weekly_time_map = performance_service.get_study_time_summary(user_id, days_ago=7)
        total_sessions_map = performance_service.get_study_session_summary(user_id, days_ago=None)
        weekly_sessions_map = performance_service.get_study_session_summary(user_id, days_ago=7)

        full_subject_models = v20_plan_data.get('subjects', [])
        cycle_to_master_id_map = {cs.id: cs.subject_id for cs in full_subject_models}

        for subject_data in processed_subjects:
            cycle_subject_id = subject_data.get('subject_id')
            master_subject_id = cycle_to_master_id_map.get(cycle_subject_id)

            if master_subject_id:
                subject_data['total_sessions'] = total_sessions_map.get(master_subject_id, 0)
                subject_data['weekly_sessions'] = weekly_sessions_map.get(master_subject_id, 0)
                subject_data['total_minutes'] = total_time_map.get(master_subject_id, 0) // 60
                subject_data['weekly_minutes'] = weekly_time_map.get(master_subject_id, 0) // 60
            else:
                subject_data['total_sessions'] = 0
                subject_data['weekly_sessions'] = 0
                subject_data['total_minutes'] = 0
                subject_data['weekly_minutes'] = 0

        self._view.populate_summary(processed_subjects)

        # --- Populate Subject Explorer Tab ---
        subjects = master_subject_service.get_all_master_subjects()
        subjects_data = []
        for subject in subjects:
            topics = master_subject_service.get_topics_for_subject(subject.id)
            subjects_data.append({
                'name': subject.name,
                'topics': [{'name': topic.name} for topic in topics]
            })
        self._view.populate_subject_explorer(subjects_data)

    def get_view(self) -> QWidget:
        return self._view