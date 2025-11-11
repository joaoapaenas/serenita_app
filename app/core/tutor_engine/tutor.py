# app/core/tutor_engine/tutor.py

import logging
from typing import Dict, Any

from app.services.interfaces import ICycleSubjectService
from .diagnoser import Diagnoser
from .human_factor_smoother import HumanFactorSmoother
from .plan_assembler import PlanAssembler
from .priority_engine import PriorityEngine
from .reasoning_engine import ReasoningEngine

log = logging.getLogger(__name__)


class Tutor:
    """
    The main v20 Cognitive Tutor Engine orchestrator. This class runs the
    entire pipeline from input to final plan generation. (v20 spec Batch 7)
    """

    def __init__(self, cycle_subject_service: ICycleSubjectService):
        self.cycle_subject_service = cycle_subject_service

    def create_study_cycle(self, cycle_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        The primary public method that runs the entire v20 pipeline.
        """
        log.info("--- Starting v20 Cognitive Tutor Engine ---")

        processed_subjects_data = []

        smoother = HumanFactorSmoother()
        cognitive_multiplier = smoother.run(
            cycle_config['human_factor_input'],
            cycle_config['human_factor_history']
        )

        all_subjects = cycle_config.get('subjects', [])
        discovery_subjects = [s for s in all_subjects if s.current_strategic_state == 'DISCOVERY']

        priority_engine = PriorityEngine(cognitive_multiplier, discovery_subjects)
        reasoning_engine = ReasoningEngine()

        for subject in all_subjects:
            log.debug(f"Processing subject: {subject.name}")

            diagnoser = Diagnoser(subject, cycle_config['study_history'])
            diagnostics = diagnoser.run()

            previous_subject_config = None
            if cycle_config.get('previous_cycle_config'):
                prev_subjects = cycle_config['previous_cycle_config'].get('subjects', [])
                previous_subject_config = next((ps for ps in prev_subjects if ps['id'] == subject.id), None)

            final_priority, flags, breakdown = priority_engine.run(subject, diagnostics, previous_subject_config)
            reasoning = reasoning_engine.generate_reasoning(diagnostics, flags)

            processed_subjects_data.append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'final_priority': final_priority,
                'reasoning': reasoning,
                'diagnostics': diagnostics,
                'priority_breakdown': breakdown,
                'reasoning_flags': flags
            })

            self.cycle_subject_service.update_cycle_subject_state(
                subject.id,
                diagnostics['strategic_mode'],
                subject.state_hysteresis_data
            )

        plan_assembler = PlanAssembler(processed_subjects_data, cycle_config)
        plan_scaffold, allocated_time_map = plan_assembler.generate_strategic_view()
        sequenced_plan = plan_assembler.generate_tactical_view(allocated_time_map)

        sorted_subjects = sorted(processed_subjects_data, key=lambda x: x['final_priority'], reverse=True)

        cycle_focus_summary = "This cycle's plan is ready."  # Fallback

        is_first_run = not cycle_config.get('study_history')

        if sorted_subjects:
            top_subject = sorted_subjects[0]
            top_subject_name = f"<b>{top_subject['subject_name']}</b>"

            if is_first_run:
                if len(sorted_subjects) > 1:
                    second_subject = sorted_subjects[1]
                    second_subject_name = f"<b>{second_subject['subject_name']}</b>"
                    cycle_focus_summary = (f"Welcome! Your first plan prioritizes {top_subject_name} to "
                                           f"start building momentum. We'll also focus on {second_subject_name} "
                                           f"to establish a baseline for your performance.")
                else:
                    cycle_focus_summary = (f"Welcome! Your first plan focuses on {top_subject_name} to "
                                           f"start strong and build momentum.")
            else:
                top_reason = top_subject['reasoning'].split('.')[0]
                if len(sorted_subjects) > 1:
                    second_subject = sorted_subjects[1]
                    second_subject_name = f"<b>{second_subject['subject_name']}</b>"
                    cycle_focus_summary = (
                        f"This cycle's main goal is to focus on {top_subject_name}: {top_reason}. "
                        f"You will also work on {second_subject_name}."
                    )
                else:
                    cycle_focus_summary = f"This cycle's main goal is to focus on {top_subject_name}: {top_reason}."

        final_plan = {
            "cycle_focus": cycle_focus_summary,
            "sequenced_plan": sequenced_plan,
            "plan_scaffold": plan_scaffold,
            "processed_subjects": sorted_subjects,
            "meta": {
                **cycle_config.get('meta', {}),
                "engine_version": "v20.1-Refactored"
            }
        }

        log.info("--- Cognitive Tutor Engine Finished ---")
        return final_plan