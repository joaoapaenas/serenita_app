# app/core/rebalance_strategies.py

from typing import Protocol, Optional, Dict, Any

from app.models.session import SubjectPerformance
from app.models.subject import CycleSubject


class IRebalanceStrategy(Protocol):
    """An interface for a single rebalancing rule."""

    def generate_suggestion(self, cycle_subject: CycleSubject, performance: SubjectPerformance) -> Optional[
        Dict[str, Any]]:
        """If the condition is met, return a suggestion dict. Otherwise, return None."""
        ...


class LowAccuracyStrategy:
    LOW_ACCURACY_THRESHOLD = 75.0
    MIN_QUESTIONS_FOR_ANALYSIS = 20

    def generate_suggestion(self, cycle_subject: CycleSubject, performance: SubjectPerformance) -> Optional[
        Dict[str, Any]]:
        if performance.total_questions < self.MIN_QUESTIONS_FOR_ANALYSIS:
            return None

        current_difficulty = cycle_subject.difficulty_weight
        if performance.accuracy < self.LOW_ACCURACY_THRESHOLD:
            new_difficulty = min(5, current_difficulty + 1)
            if new_difficulty != current_difficulty:
                return {
                    "reason": f"Low Accuracy ({performance.accuracy:.1f}%)",
                    "new_difficulty": new_difficulty
                }
        return None


class HighAccuracyStrategy:
    HIGH_ACCURACY_THRESHOLD = 92.0
    MIN_QUESTIONS_FOR_ANALYSIS = 20

    def generate_suggestion(self, cycle_subject: CycleSubject, performance: SubjectPerformance) -> Optional[
        Dict[str, Any]]:
        if performance.total_questions < self.MIN_QUESTIONS_FOR_ANALYSIS:
            return None

        current_difficulty = cycle_subject.difficulty_weight
        if performance.accuracy > self.HIGH_ACCURACY_THRESHOLD:
            new_difficulty = max(1, current_difficulty - 1)
            if new_difficulty != current_difficulty:
                return {
                    "reason": f"High Accuracy ({performance.accuracy:.1f}%)",
                    "new_difficulty": new_difficulty
                }
        return None
