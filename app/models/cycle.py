# app/models/cycle.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Cycle:
    """Represents a single Study Cycle, including its scheduling rules."""
    id: int
    exam_id: int
    name: str
    # All field names updated to snake_case
    block_duration_min: int
    current_queue_position: int
    is_active: bool
    is_continuous: bool
    daily_goal_blocks: int
    phase: str
    created_at: str
    updated_at: str
    soft_delete: bool
    deleted_at: Optional[str]
    timing_strategy: str = "Adaptive"
    plan_cache_json: Optional[str] = None
