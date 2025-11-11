# app/models/session.py

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class SubjectPerformance:
    """Aggregated performance statistics for a subject."""
    # Field names updated to snake_case
    subject_name: str
    total_questions: int
    total_correct: int

    @property
    def accuracy(self) -> float:
        if self.total_questions == 0: return 0.0
        return (self.total_correct / self.total_questions) * 100


@dataclass
class StudyActivity:
    """Represents a single, atomic activity within a study session (T, P, or R)."""
    id: int
    session_id: int
    # All field names updated to snake_case
    topic_id: Optional[int]
    activity_type_id: int
    start_time: str
    end_time: Optional[str]
    duration_sec: int
    questions_done: Optional[int]
    questions_correct: Optional[int]

    @property
    def accuracy(self) -> float:
        if self.questions_done is None or self.questions_done == 0: return 0.0
        correct = self.questions_correct or 0
        return (correct / self.questions_done) * 100


@dataclass
class QuestionPerformance:
    """Represents a single question answered during a session, as per v20 spec."""
    id: int  # DB primary key
    session_id: int
    topic_name: str
    difficulty_level: int
    is_correct: bool


@dataclass
class StudySession:
    """Represents a complete study session from start to finish."""
    id: int
    subject_id: int
    start_time: str
    user_id: Optional[int]
    cycle_id: Optional[int]
    topic_id: Optional[int]
    end_time: Optional[str]
    total_duration_sec: int
    total_pause_duration_sec: int
    liquid_duration_sec: int
    total_questions_done: int = 0
    total_questions_correct: int = 0
    description: Optional[str] = None
    study_method: Optional[str] = None
    soft_delete: bool = False
    deleted_at: Optional[str] = None
    subject_name: Optional[str] = None
    user_feedback_effectiveness: Optional[int] = None  # 1-5, as per v20 spec
    questions: List[QuestionPerformance] = field(default_factory=list)


@dataclass
class ReviewTask:
    """Represents a scheduled spaced repetition review."""
    id: int
    topic_id: int
    original_study_activity_id: int
    scheduled_date: str
    review_type_id: int
    status_id: int
    completed_date: Optional[str]
