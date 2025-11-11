# app/core/tutor_engine/priority_engine.py

import logging
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional

from app.models.subject import CycleSubject

log = logging.getLogger(__name__)


class PriorityEngine:
    """
    Calculates a subject's final_priority score by determining a base_priority
    and passing it through a pipeline of tactical modifiers. (v20 spec Batch 4)
    """
    MAX_DISCOVERY_BOOSTS_PER_CYCLE = 2
    ROI_TIME_THRESHOLD_HR = 20
    ROI_VELOCITY_THRESHOLD = 0.01
    ROI_POINT_VALUE_THRESHOLD = 3

    def __init__(self, cognitive_capacity_multiplier: float, all_discovery_subjects: list):
        self.cognitive_multiplier = cognitive_capacity_multiplier
        self.reasoning_flags = {}
        self._setup_discovery_boost(all_discovery_subjects)

    def _setup_discovery_boost(self, all_discovery_subjects: list):
        """Identifies subjects that will get the discovery boost, per spec 4.2.1."""
        sorted_discovery = sorted(
            all_discovery_subjects,
            key=lambda s: (s.date_added or '9999-99-99', -s.relevance_weight)
        )
        self.boosted_subject_ids = {
            s.id for s in sorted_discovery[:self.MAX_DISCOVERY_BOOSTS_PER_CYCLE]
        }
        log.debug(f"Subjects receiving discovery boost: {self.boosted_subject_ids}")

    def run(self, subject: CycleSubject, diagnostics: dict, previous_subject_config: Optional[dict]) -> Tuple[float, dict, dict]:
        """Calculates final_priority and returns reasoning flags and calculation breakdown."""
        self.reasoning_flags = {}  # Reset for each subject
        base_priority, breakdown = self._calculate_base_priority(subject, diagnostics)
        final_priority = self._run_tactical_modifiers(base_priority, subject, diagnostics, previous_subject_config)
        return final_priority, self.reasoning_flags, breakdown

    def _calculate_base_priority(self, subject: CycleSubject, diagnostics: dict) -> Tuple[float, dict]:
        """Selects a strategy based on strategic_mode and executes its formula. (Spec 4.1.2)"""
        mode = diagnostics['strategic_mode']
        confidence = diagnostics['mastery_confidence_score']
        mastery = diagnostics['durable_mastery_score']
        durability = diagnostics['durability_factor']
        points = subject.relevance_weight

        confidence_modulator = 0.4 + (0.6 * confidence)
        priority = 0.0

        if mode == 'DISCOVERY':
            priority = 50 + (points * 10)
        elif mode == 'DEEP_WORK':
            priority = (50 + (points * 5) + (1.0 - mastery) * 50) * confidence_modulator
        elif mode == 'CONQUER':
            priority = (90 + mastery * 20 + points * 2) * confidence_modulator
        elif mode == 'CEMENT':
            priority = (40 + (1.0 - durability) * 40 + points * 3) * confidence_modulator
        elif mode == 'MAINTAIN':
            priority = (10 + points * 2) * confidence_modulator

        base_priority = priority * self.cognitive_multiplier

        priority_breakdown = {
            'base_score': priority,
            'cognitive_multiplier': self.cognitive_multiplier,
            'confidence_modulator': confidence_modulator
        }
        return base_priority, priority_breakdown

    def _run_tactical_modifiers(self, base_priority: float, subject: CycleSubject, diagnostics: dict,
                                previous_cycle_config: Optional[dict]) -> float:
        """Applies the tactical modifier pipeline from spec 4.2."""
        final_priority = base_priority

        if diagnostics['strategic_mode'] == 'DISCOVERY' and subject.id in self.boosted_subject_ids:
            final_priority *= 1.5
            self.reasoning_flags['discovery_boost_applied'] = True

        if diagnostics['strategic_mode'] == 'CONQUER' and \
                subject.relevance_weight <= self.ROI_POINT_VALUE_THRESHOLD and \
                diagnostics['total_time_invested_hr'] > self.ROI_TIME_THRESHOLD_HR and \
                diagnostics['learning_velocity'] < self.ROI_VELOCITY_THRESHOLD:
            final_priority *= 0.25
            self.reasoning_flags['roi_warning'] = True
            log.warning(f"ROI Warning triggered for subject '{subject.name}'.")

        if previous_cycle_config and 'subjects' in previous_cycle_config:
            previous_subjects_list = previous_cycle_config['subjects']
            previous_subject_data = next((s for s in previous_subjects_list if s['id'] == subject.id), None)

            if previous_subject_data:
                current_points = subject.relevance_weight
                previous_points = previous_subject_data.get('relevance_weight', current_points)
                if current_points > previous_points:
                    final_priority += 50
                    self.reasoning_flags['urgency_shock'] = True
                    log.info(f"Urgency Shock triggered for subject '{subject.name}'.")

        # Apply a deprioritization modifier for subjects with recent study time
        # This ensures that subjects that have been recently studied are deprioritized
        total_time_hr = diagnostics.get('total_time_invested_hr', 0)
        if total_time_hr > 0:
            # Get recent study time (last 24 hours)
            recent_time_modifier = self._calculate_recent_study_time_modifier(subject)
            final_priority *= recent_time_modifier

        return final_priority

    def _calculate_recent_study_time_modifier(self, subject: CycleSubject) -> float:
        """
        Calculate a modifier based on recent study time to deprioritize subjects
        that have been studied recently.
        """
        # For now, we'll use a simple approach that reduces priority based on recent time
        # In a more sophisticated implementation, we would analyze the actual session history

        # Placeholder implementation - in a real implementation, we would analyze
        # the actual recent sessions for this subject
        return 1.0  # No modification for now