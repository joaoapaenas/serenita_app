# app/services/interfaces.py
from dataclasses import dataclass
from typing import Protocol, List, Optional

from app.models.cycle import Cycle
from app.models.exam import Exam
from app.models.session import SubjectPerformance, QuestionPerformance, StudySession
from app.models.subject import Subject, Topic, CycleSubject, WorkUnit
from app.models.user import User, HumanFactor


class IMasterSubjectService(Protocol):
    """Manages global, master subject definitions."""

    def get_master_subject_by_name(self, name: str) -> Optional[Subject]: ...

    def get_all_master_subjects(self) -> List[Subject]: ...

    def get_subject_by_id(self, subject_id: int) -> Optional[Subject]: ...

    def create(self, name: str) -> int | None: ...

    def update(self, subject_id: int, name: str): ...

    def delete(self, subject_id: int): ...

    def get_topics_for_subject(self, subject_id: int) -> List[Topic]: ...


class ICycleSubjectService(Protocol):
    """Manages subjects within the context of a specific cycle."""

    def add_subject_to_cycle(self, cycle_id: int, subject_id: int, weights: dict, calculated_data: dict): ...

    def get_subjects_for_cycle(self, cycle_id: int) -> List[CycleSubject]: ...

    def get_cycle_subject(self, cycle_subject_id: int) -> Optional[CycleSubject]: ...

    def delete_subjects_for_cycle(self, cycle_id: int): ...

    def update_cycle_subject_difficulty(self, cycle_subject_id: int, new_difficulty: int): ...

    def update_cycle_subject_calculated_fields(self, cycle_subject_id: int, final_weight: float, num_blocks: int): ...

    def update_cycle_subject_state(self, cycle_subject_id: int, state: str, hysteresis_data: dict): ...


class IStudyQueueService(Protocol):
    """Manages the creation and retrieval of the study queue for a cycle."""

    def save_queue(self, cycle_id: int, queue: List[int]): ...

    def get_next_in_queue(self, cycle_id: int, position: int) -> Optional[CycleSubject]: ...


class IWorkUnitService(Protocol):
    """Manages the tactical work units associated with a subject."""

    def get_work_units_for_subject(self, subject_id: int) -> List[WorkUnit]: ...

    def add_work_unit(self, subject_id: int, unit_data: dict) -> Optional[WorkUnit]: ...

    def update_work_unit(self, unit_id: int, unit_data: dict) -> bool: ...

    def delete_work_unit(self, unit_id: int): ...

    def update_work_unit_status(self, work_unit_id: int, is_completed: bool): ...

    def add_topics_bulk(self, subject_id: int, topic_names: List[str]): ...


class ITemplateSubjectService(Protocol):
    """Manages subjects related to exam templates."""

    def get_subjects_for_template(self, exam_id: int) -> List[dict]: ...


class ICycleService(Protocol):
    """Defines the contract for cycle-related data operations."""

    def create(self, name: str, block_duration: int, is_continuous: bool, daily_goal: int, exam_id: int,
               timing_strategy: str) -> int: ...

    def get_active(self) -> Optional[Cycle]: ...

    def get_all_for_exam(self, exam_id: int) -> List[Cycle]: ...

    def get_by_id(self, cycle_id: int) -> Optional[Cycle]: ...

    def set_active(self, cycle_id: int): ...

    def set_all_inactive(self): ...

    def soft_delete(self, cycle_id: int): ...

    def restore_soft_deleted(self, cycle_id: int): ...

    def update_properties(self, cycle_id: int, name: str, block_duration: int, is_continuous: bool,
                          daily_goal: int, is_active: bool, timing_strategy: str): ...

    def advance_queue_position(self, cycle_id: int): ...

    def save_plan_cache(self, cycle_id: int, plan_data: dict): ...

    def get_plan_cache(self, cycle_id: int) -> Optional[dict]: ...


class ISessionService(Protocol):
    """Defines the contract for study session and activity logging."""

    def start_session(self, user_id: int, subject_id: int, cycle_id: int = None, topic_id: int = None) -> int: ...

    def finish_session(self, session_id: int, description: str = None, questions: List[QuestionPerformance] = None,
                       topic_id: int | None = None): ...

    def log_manual_session(self, user_id: int, cycle_id: int, subject_id: int, topic_id: Optional[int],
                           start_datetime_iso: str, duration_minutes: int, description: str,
                           questions: Optional[List[QuestionPerformance]] = None) -> int: ...

    def add_pause_start(self, session_id: int) -> int: ...

    def add_pause_end(self, session_id: int): ...

    def log_activity_and_create_reviews(self, session_id: int, topic_id: int | None, activity_type: str,
                                        duration_sec: int, perf_data: dict): ...

    def get_history_for_cycle(self, cycle_id: int) -> List[StudySession]: ...

    def get_completed_session_count(self, cycle_id: int) -> int: ...


class IPerformanceService(Protocol):
    """Defines the contract for performance data aggregation."""

    def get_summary(self, cycle_id: int) -> List[SubjectPerformance]: ...

    def get_performance_over_time(self, user_id: int, subject_id: int | None = None) -> List[dict]:
        """
        Retrieves daily aggregated performance data for graphing.
        Returns a list of dicts: {'date': str, 'total_questions': int, 'total_correct': int}
        """
        ...

    def get_subjects_with_performance_data(self, user_id: int) -> List[dict]:
        """
        Retrieves a list of subjects for which a user has performance data.
        Returns a list of dicts: [{'id': int, 'name': str}]
        """
        ...

    def get_topic_performance(self, user_id: int, subject_id: int, days_ago: int | None = None) -> List[dict]:
        """
        Retrieves topic-level performance for a specific subject.
        Returns a list of dicts: {'topic_name': str, 'total_questions': int, 'total_correct': int, 'accuracy': float}
        """
        ...

    def get_work_unit_summary(self, user_id: int, subject_id: int | None = None) -> dict:
        """
        Retrieves a summary of work unit completion.
        Returns a dict: {'total_units': int, 'completed_units': int}
        """
        ...

    def get_study_time_summary(self, user_id: int, days_ago: int) -> dict[int, int]:
        """
        Retrieves total study time per subject over a given period.
        Returns a dictionary mapping {subject_id: total_seconds}.
        """
        ...

    def get_study_session_summary(self, user_id: int, days_ago: int | None = None) -> dict[int, int]:
        """
        Retrieves total study sessions per subject over a given period.
        Returns a dictionary mapping {subject_id: session_count}.
        """
        ...

    def get_subject_summary_for_analytics(self, user_id: int, cycle_id: int, days_ago: int | None = None) -> List[dict]:
        """
        Retrieves a comprehensive summary for each subject for the analytics screen.
        """
        ...


class IExamService(Protocol):
    """Defines the contract for exam-related data operations."""

    def create(self, user_id: int, name: str, institution: str = "", role: str = "", exam_board: str = "",
               area: str = "", status: str = "PREVISTO", exam_date: str = None,
               has_edital: int = 0, predicted_exam_date: str = None) -> int: ...

    def get_by_id(self, exam_id: int) -> Optional[Exam]: ...

    def get_all_for_user(self, user_id: int) -> List[Exam]: ...

    def update(self, exam_id: int, name: str, institution: str, role: str, exam_board: str, area: str, status: str,
               exam_date: str, has_edital: int, predicted_exam_date: str): ...

    def soft_delete(self, exam_id: int): ...

    def get_available_templates(self) -> List[Exam]: ...


class IUserService(Protocol):
    """Defines the contract for user-related data operations."""

    def create_user(self, name: str, study_level: str) -> Optional[User]: ...

    def get_user(self, user_id: int) -> Optional[User]: ...

    def get_first_user(self) -> Optional[User]: ...

    def save_human_factor(self, user_id: int, date: str, energy: str, stress: str) -> int: ...

    def get_human_factor_history(self, user_id: int, limit: int = 20) -> List[HumanFactor]: ...

    def update_user(self, user_id: int, name: str, study_level: str, theme: str) -> Optional[User]: ...

@dataclass
class DailyPerformance:
    date: str  # 'YYYY-MM-DD'
    questions_done: int
    questions_correct: int

# --- FIX: Define WeeklyPerformance BEFORE it is used in IAnalyticsService ---
@dataclass
class WeeklyPerformance:
    week_start_date: str # 'YYYY-MM-DD'
    questions_done: int
    questions_correct: int
    avg_per_day: float

class IAnalyticsService(Protocol):
    """Defines the contract for time-series performance analytics."""
    def get_daily_performance(self, cycle_id: int, days_ago: Optional[int] = None) -> List[DailyPerformance]: ...
    def get_weekly_summary(self, cycle_id: int, days_ago: Optional[int] = None) -> List[WeeklyPerformance]: ...
    def get_overall_summary(self, cycle_id: int) -> dict: ...