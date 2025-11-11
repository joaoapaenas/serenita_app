# app/models/user.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Represents a user profile in the application."""
    id: int
    name: str
    description: Optional[str]
    # Field names updated to snake_case
    study_level: Optional[str]
    theme: str # Added theme preference
    created_at: str


@dataclass
class HumanFactor:
    """Represents the user's self-reported state for a given day, as per v20 spec."""
    id: int  # DB primary key
    user_id: int
    date: str  # 'YYYY-MM-DD'
    energy_level: str  # 'High', 'Normal', 'Low'
    stress_level: str  # 'High', 'Normal', 'Low'