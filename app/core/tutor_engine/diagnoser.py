import logging
import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import List

from app.models.session import StudySession
from app.models.subject import CycleSubject
from . import tutor_config as config

log = logging.getLogger(__name__)


class Diagnoser:
    """
    Analyzes a subject's history and state
    """

    def __init__(self, subject: CycleSubject, study_history: List[StudySession]):
        self.subject = subject
        self.subject_history = self._filter_history(study_history)

    def _filter_history(self, full_history: List[StudySession]) -> List[StudySession]:
        """Isolates session records relevant to the current subject."""
        # In our DB schema, sessions are already linked to a subject_id.
        # This is a placeholder for more complex filtering if needed in the future.
        return [s for s in full_history if s.subject_id == self.subject.subject_id]

    def run(self) -> dict:
        """
        Main execution method. Runs all diagnostic steps and returns the
        v20_Diagnostics package.
        """
        if not self.subject_history:
            log.debug(f"No history for subject '{self.subject.name}'. Using default diagnostics.")
            return self._default_diagnostics()

        perf_metrics = self._calculate_performance_metrics()
        confidence = self._calculate_confidence_score(perf_metrics)
        strategic_mode = self._assign_strategic_mode(perf_metrics)

        # Update the hysteresis data for the next cycle
        self._update_hysteresis_data(strategic_mode, perf_metrics['durable_mastery_score'])

        diagnostics = {
            "strategic_mode": strategic_mode,
            "mastery_confidence_score": confidence,
            **perf_metrics
        }
        return diagnostics

    def _calculate_performance_metrics(self) -> dict:
        """Implements logic from v20.md section 3.3.2."""
        total_time_min = sum(s.liquid_duration_sec for s in self.subject_history) / 60
        total_time_hr = total_time_min / 60

        all_questions = [q for s in self.subject_history for q in s.questions]

        if not all_questions:
            # We still have valid time-invested data even with no questions.
            # Use the default metrics as a template but overwrite the time.
            metrics = self._default_performance_metrics()
            metrics["total_time_invested_hr"] = total_time_hr
            return metrics

        today_date = datetime.now(timezone.utc).date()

        weighted_scores = []
        weights = []
        for session in self.subject_history:
            try:
                session_date = datetime.fromisoformat(session.start_time).date()
                days_ago = (today_date - session_date).days
                weight = math.exp(-config.DECAY_RATE * days_ago)
                weights.append(weight)
                for q in session.questions:
                    weighted_scores.append(q.is_correct * weight)
            except (ValueError, TypeError):
                continue  # Skip sessions with invalid date formats

        durable_mastery_score = (sum(weighted_scores) / len(weighted_scores)) if weighted_scores else 0.0
        durability_factor = sum(weights) / len(weights) if weights else 0.0

        # Calculate mastery_by_topic
        mastery_by_topic = defaultdict(lambda: {'correct': 0, 'total': 0})
        for q in all_questions:
            mastery_by_topic[q.topic_name]['correct'] += q.is_correct
            mastery_by_topic[q.topic_name]['total'] += 1

        final_mastery_by_topic = {
            topic: data['correct'] / data['total'] if data['total'] > 0 else 0.0
            for topic, data in mastery_by_topic.items()
        }

        # Calculate learning_velocity
        learning_velocity = durable_mastery_score / total_time_hr if total_time_hr > 0 else 0.0

        # --- FIX: Calculate effectiveness_metrics ---
        effectiveness_by_method = defaultdict(lambda: {'total_score': 0, 'count': 0})
        for session in self.subject_history:
            if session.study_method and session.user_feedback_effectiveness is not None:
                method = session.study_method
                effectiveness_by_method[method]['total_score'] += session.user_feedback_effectiveness
                effectiveness_by_method[method]['count'] += 1

        final_effectiveness_metrics = {
            method: data['total_score'] / data['count']
            for method, data in effectiveness_by_method.items()
            if data['count'] > 0
        }
        # --- END FIX ---

        return {
            "durable_mastery_score": durable_mastery_score,
            "durability_factor": durability_factor,
            "learning_velocity": learning_velocity,
            "total_time_invested_hr": total_time_hr,
            "total_questions": len(all_questions),
            "mastery_by_topic": final_mastery_by_topic,
            "effectiveness_metrics": final_effectiveness_metrics
        }

    def _calculate_confidence_score(self, perf_metrics: dict) -> float:
        """Implements logic from v20.md section 3.3.3."""
        # 1. Confidence from Volume
        total_questions = perf_metrics['total_questions']
        c_volume = math.log10(total_questions + 1) / math.log10(config.TARGET_QUESTIONS_FOR_CONFIDENCE + 1)
        c_volume = min(c_volume, 1.0)  # Cap at 1.0

        # 2. Confidence from Recency (is the durability_factor)
        c_recency = perf_metrics['durability_factor']

        # 3. Confidence from Granularity
        # This requires more detailed data than we currently log (time per question).
        # We will use a placeholder for now, assuming all time had questions.
        c_granularity = 1.0  # Placeholder

        # Weighted average (equal weights for now)
        mastery_confidence_score = (c_volume + c_recency + c_granularity) / 3.0
        return mastery_confidence_score

    def _assign_strategic_mode(self, perf_metrics: dict) -> str:
        """Implements two-step (Propose -> Hysteresis Gate) logic from 3.3.4"""
        # Step A: Propose a mode
        proposed_mode = self._propose_mode(
            perf_metrics['durable_mastery_score'],
            perf_metrics['durability_factor'],
            perf_metrics['total_time_invested_hr']
        )

        # Step B: Apply Hysteresis Gate
        final_mode = self._apply_hysteresis_gate(proposed_mode, perf_metrics['durable_mastery_score'])
        return final_mode

    def _propose_mode(self, durable_mastery, durability_factor=0, time_hr=0) -> str:
        """v20.md section 3.3.4 Step A"""
        if time_hr < 1.0 and durable_mastery < 0.1:
            return 'DISCOVERY'
        elif durable_mastery >= config.MASTERY_TARGET and durability_factor > 0.7:
            return 'MAINTAIN'
        elif durable_mastery >= config.MASTERY_TARGET:
            return 'CEMENT'
        elif durable_mastery >= config.CONQUER_THRESHOLD:
            return 'CONQUER'
        else:
            return 'DEEP_WORK'

    def _apply_hysteresis_gate(self, proposed_mode: str, current_mastery: float) -> str:
        """v20.md section 3.3.4 Step B - Veto logic"""
        previous_mode = self.subject.current_strategic_state
        if previous_mode not in config.STATE_PROGRESSION:
            return proposed_mode  # No valid previous state to compare against

        previous_idx = config.STATE_PROGRESSION.index(previous_mode)
        proposed_idx = config.STATE_PROGRESSION.index(proposed_mode)

        # A "regression" is moving to a state earlier in the list
        is_regression = proposed_idx < previous_idx

        # Check if there's been significant recent progress
        has_significant_progress = self._has_significant_recent_progress()

        # Allow transitions if there's significant progress, regardless of direction
        if has_significant_progress:
            log.debug(f"Allowing mode transition for '{self.subject.name}' due to significant recent progress.")
            return proposed_mode

        if not is_regression:
            return proposed_mode

        # Conditions for allowing a regression:
        hysteresis = self.subject.state_hysteresis_data

        # 1. Has been in the current state for enough cycles
        if hysteresis.get('consecutive_cycles_in_state', 0) >= config.MIN_CYCLES_IN_STATE_FOR_REGRESSION:
            log.debug(f"Allowing regression to '{proposed_mode}' for '{self.subject.name}' (reason: tenure in state).")
            return proposed_mode

        # 2. Has there been a significant drop in mastery?
        last_mastery = hysteresis.get('last_mastery_score', 0.0)
        mastery_drop = last_mastery - current_mastery
        if last_mastery > 0 and (mastery_drop / last_mastery) > config.MASTERY_DROP_THRESHOLD_FOR_REGRESSION:
            log.debug(
                f"Allowing regression to '{proposed_mode}' for '{self.subject.name}' (reason: significant mastery drop).")
            return proposed_mode

        # Otherwise, veto the regression
        log.info(f"VETOED regression from '{previous_mode}' to '{proposed_mode}' for subject '{self.subject.name}'.")
        return previous_mode

    def _has_significant_recent_progress(self) -> bool:
        """
        Check if there has been significant recent progress that should trigger a state transition.
        This is to ensure that when a user completes a session, the subject's state can update appropriately.
        """
        # If there's no history, there's no progress to measure
        if not self.subject_history:
            return False

        # Get the most recent session
        recent_sessions = sorted(self.subject_history, key=lambda s: s.start_time, reverse=True)[:3]

        # If we have recent sessions, check if they represent significant progress
        if recent_sessions:
            # Calculate total time in recent sessions
            recent_time_hr = sum(s.liquid_duration_sec for s in recent_sessions) / 3600

            # If recent time is significant (more than 2 hours), consider it progress
            if recent_time_hr > 2.0:
                log.debug(f"Significant recent progress detected for '{self.subject.name}' ({recent_time_hr:.1f} hours)")
                return True

        return False

    def _update_hysteresis_data(self, final_mode: str, current_mastery: float):
        """Updates the subject's hysteresis data based on the final mode."""
        previous_mode = self.subject.current_strategic_state
        hysteresis = self.subject.state_hysteresis_data

        if final_mode == previous_mode:
            hysteresis['consecutive_cycles_in_state'] = hysteresis.get('consecutive_cycles_in_state', 0) + 1
        else:
            hysteresis['consecutive_cycles_in_state'] = 1
            hysteresis['last_transition_date'] = datetime.now(timezone.utc).isoformat()

        hysteresis['last_mastery_score'] = current_mastery
        # The subject object is updated in-place. The orchestrator will persist this.

    def _default_diagnostics(self) -> dict:
        """Returns a default diagnostic package for subjects with no history."""
        return {
            "strategic_mode": 'DISCOVERY',
            "mastery_confidence_score": 0.0,
            **self._default_performance_metrics()
        }

    @staticmethod
    def _default_performance_metrics() -> dict:
        """Default performance metrics for subjects with no question data."""
        return {
            "durable_mastery_score": 0.0,
            "durability_factor": 0.0,
            "learning_velocity": 0.0,
            "total_time_invested_hr": 0.0,
            "total_questions": 0,
            "mastery_by_topic": {},
            "effectiveness_metrics": {}
        }