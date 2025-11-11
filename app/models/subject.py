# app/models/subject.py

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Subject:
    """Represents a global, master subject."""
    id: int
    name: str
    color: Optional[str]
    # REMOVED: strategic_state_id is redundant; state is managed per-cycle now.
    created_at: str
    updated_at: str
    soft_delete: bool
    deleted_at: Optional[str]


@dataclass
class Topic:
    """Represents a specific topic within a parent Subject."""
    id: int
    subject_id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str
    soft_delete: bool
    deleted_at: Optional[str]


@dataclass
class WorkUnit:
    """
    Represents a discrete, plannable task within a subject, as per v20 spec.
    e.g., reading a chapter, completing a problem set.
    """
    id: int  # DB primary key
    subject_id: int
    unit_id: str  # Machine-readable ID from v20 spec (e.g., "wu_calc1_ch1_reading")
    title: str
    type: str  # e.g., 'reading', 'problem_set'
    estimated_time_minutes: int
    is_completed: bool
    related_questions_topic: str  # Links to performance data
    sequence_order: int  # For ordering within a subject

    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "unit_id": self.unit_id,
            "title": self.title,
            "type": self.type,
            "estimated_time_minutes": self.estimated_time_minutes,
            "is_completed": self.is_completed,
            "related_questions_topic": self.related_questions_topic,
            "sequence_order": self.sequence_order,
        }


@dataclass
class CycleSubject:
    """Represents a Subject in the context of a specific StudyCycle."""
    id: int
    cycle_id: int
    subject_id: int
    relevance_weight: int  # Corresponds to v20 'point_value'
    volume_weight: int
    difficulty_weight: int
    is_active: bool
    final_weight_calc: float
    num_blocks_in_cycle: int
    name: Optional[str] = None
    color: Optional[str] = None

    date_added: Optional[str] = None  # 'YYYY-MM-DD'
    current_strategic_state: Optional[str] = 'DISCOVERY'  # e.g., 'DEEP_WORK', 'MAINTAIN'

    # Nested dict for state hysteresis data
    state_hysteresis_data: dict = field(default_factory=lambda: {
        'consecutive_cycles_in_state': 0,
        'last_transition_date': None,
        'last_mastery_score': 0.0
    })

    # A list of specific tasks within this subject for this cycle
    work_units: List[WorkUnit] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "cycle_id": self.cycle_id,
            "subject_id": self.subject_id,
            "relevance_weight": self.relevance_weight,
            "volume_weight": self.volume_weight,
            "difficulty_weight": self.difficulty_weight,
            "is_active": self.is_active,
            "final_weight_calc": self.final_weight_calc,
            "num_blocks_in_cycle": self.num_blocks_in_cycle,
            "name": self.name,
            "color": self.color,
            "date_added": self.date_added,
            "current_strategic_state": self.current_strategic_state,
            "state_hysteresis_data": self.state_hysteresis_data,
            "work_units": [wu.to_dict() for wu in self.work_units],
        }