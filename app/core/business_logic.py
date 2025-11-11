# app/core/business_logic.py

import logging
import random
from typing import List

from app.core.tutor_engine.rebalance_strategies import IRebalanceStrategy, LowAccuracyStrategy, HighAccuracyStrategy
from app.models.session import SubjectPerformance
from app.models.subject import CycleSubject

log = logging.getLogger(__name__)


def calculate_final_weight(relevance: int, volume: int, difficulty: int) -> float:
    """
    Calculates the weighted average for a subject's importance in a cycle.
    """
    w_relevance = 0.5
    w_volume = 0.2
    w_difficulty = 0.3
    final_weight = (relevance * w_relevance) + (volume * w_volume) + (difficulty * w_difficulty)
    log.info(f"final_weight:'{final_weight}'")
    return final_weight


def calculate_num_blocks(final_weight: float) -> int:
    """
    Determines the number of study blocks for a subject in a cycle based
    on its final calculated weight.
    """
    return round(final_weight)


def generate_study_queue(cycle_subjects: List[CycleSubject]) -> List[int]:
    """
    Creates a randomized playlist of IDs from the CycleSubjects table.
    The number of times each ID appears is based on its 'num_blocks_in_cycle'.
    """
    playlist = []
    for cycle_subject in cycle_subjects:
        # The ID for the queue must come from the CycleSubject object
        # (the id from the junction table), as this uniquely identifies
        # the subject *within this specific cycle*.
        playlist.extend([cycle_subject.id] * cycle_subject.num_blocks_in_cycle)
    random.shuffle(playlist)
    log.info(f"generate_study_queue:'{playlist}'")
    return playlist


def suggest_rebalance(cycle_subjects: List[CycleSubject], performance_summary: List[SubjectPerformance]) -> List[dict]:
    """
    Analyzes performance and suggests changes to subject difficulty weights.
    This now uses the Strategy pattern to allow for easy extension of rules.
    """
    suggestions = []
    # The list of rules to apply. To add a new rule, just add a new class instance here!
    strategies: List[IRebalanceStrategy] = [
        LowAccuracyStrategy(),
        HighAccuracyStrategy(),
        # e.g., NotStudiedRecentlyStrategy() could be added here in the future
    ]

    performance_map = {perf.subject_name: perf for perf in performance_summary}

    for cycle_subject in cycle_subjects:
        if cycle_subject.name not in performance_map:
            continue

        perf = performance_map[cycle_subject.name]

        for strategy in strategies:
            suggestion_data = strategy.generate_suggestion(cycle_subject, perf)
            if suggestion_data:
                suggestions.append({
                    "cycle_subject_id": cycle_subject.id,
                    "subject_name": cycle_subject.name,
                    "old_difficulty": cycle_subject.difficulty_weight,
                    **suggestion_data  # Unpack the reason and new_difficulty
                })
                # We found a suggestion, so we can stop checking other strategies for this subject
                break

    log.info(f"generate suggestions:'{suggestions}'")
    return suggestions
