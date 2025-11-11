# app/models/exam.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Exam:
    """Represents a specific exam goal (a 'exam')."""
    id: int
    user_id: int
    name: str
    institution: Optional[str]
    exam_board: Optional[str]
    role: Optional[str]
    area: Optional[str]
    status: str
    has_edital: int
    predicted_exam_date: Optional[str]
    exam_date: Optional[str]
    created_at: str
    updated_at: str
    soft_delete: bool
    deleted_at: Optional[str]
