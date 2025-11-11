# app/core/tutor_engine/input_assembler.py
import logging
from datetime import date
from typing import Dict, Any

from app.models.cycle import Cycle
from app.models.user import User
from app.services.interfaces import (ICycleService, ICycleSubjectService, IWorkUnitService,
                                     ISessionService, IUserService)

log = logging.getLogger(__name__)


class V20InputAssembler:
    """
    Responsible for gathering all necessary data from various services
    and assembling the input configuration dictionary for the v20 Tutor engine.
    This adheres to SRP by separating data assembly from controller logic.
    """

    def __init__(self, cycle_service: ICycleService, cycle_subject_service: ICycleSubjectService,
                 work_unit_service: IWorkUnitService, session_service: ISessionService,
                 user_service: IUserService):
        self.cycle_service = cycle_service
        self.cycle_subject_service = cycle_subject_service
        self.work_unit_service = work_unit_service
        self.session_service = session_service
        self.user_service = user_service

    def assemble(self, active_cycle: Cycle, current_user: User) -> Dict[str, Any]:
        """
        Gathers data from all sources and constructs the final dictionary.
        """
        log.debug(f"Assembling v20 input for cycle_id: {active_cycle.id} and user_id: {current_user.id}")

        subjects_in_cycle = self.cycle_subject_service.get_subjects_for_cycle(active_cycle.id)
        for subject in subjects_in_cycle:
            # Enrich the cycle subject models with their associated work units
            subject.work_units = self.work_unit_service.get_work_units_for_subject(subject.subject_id)

        study_history = self.session_service.get_history_for_cycle(active_cycle.id)
        human_factor_history = self.user_service.get_human_factor_history(current_user.id)

        today_str = date.today().isoformat()
        current_human_factor = next((h for h in human_factor_history if h.date == today_str), None)

        if current_human_factor:
            current_human_factor_dict = {
                'date': current_human_factor.date,
                'energy_level': current_human_factor.energy_level,
                'stress_level': current_human_factor.stress_level
            }
        else:
            current_human_factor_dict = {
                'date': today_str,
                'energy_level': 'Normal',
                'stress_level': 'Normal'
            }

        previous_cycle_config = self.cycle_service.get_plan_cache(active_cycle.id) or {}

        return {
            "subjects": subjects_in_cycle,
            "study_history": study_history,
            "available_time_minutes": active_cycle.daily_goal_blocks * active_cycle.block_duration_min,
            "cycle_duration_days": 7,  # This could be made dynamic in the future
            "human_factor_input": current_human_factor_dict,
            "human_factor_history": human_factor_history,
            "previous_cycle_config": previous_cycle_config,
            "meta": {"human_factor_input": current_human_factor_dict}
        }