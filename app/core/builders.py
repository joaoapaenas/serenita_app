# app/core/builders.py

import logging
from typing import List, Dict, Any, Optional

from app.core import business_logic

from app.services.interfaces import (ICycleService, ICycleSubjectService, IStudyQueueService, IMasterSubjectService)

log = logging.getLogger(__name__)


class CycleBuilder:
    """
    Encapsulates the complex logic of building a fully-formed study cycle.
    It handles creation, subject association, calculations, and queue generation.
    """

    def __init__(self,
                 cycle_service: ICycleService,
                 cycle_subject_service: ICycleSubjectService,
                 master_subject_service: IMasterSubjectService,
                 queue_service: IStudyQueueService):
        self._cycle_service = cycle_service
        self._cycle_subject_service = cycle_subject_service
        self._master_subject_service = master_subject_service
        self._queue_service = queue_service
        self._subject_order: List[str] = []

        self._cycle_id: Optional[int] = None
        self._exam_id: Optional[int] = None
        self._cycle_data: Dict[str, Any] = {}
        self._subjects_data: List[Dict[str, Any]] = []

    def for_exam(self, exam_id: int) -> 'CycleBuilder':
        """Sets the parent exam for a new cycle."""
        self._exam_id = exam_id
        return self

    def with_properties(self, cycle_data: Dict[str, Any]) -> 'CycleBuilder':
        """Sets the core properties of the cycle (name, duration, etc.)."""
        self._cycle_data = cycle_data
        return self

    def with_subjects(self, subjects_data: List[Dict[str, Any]]) -> 'CycleBuilder':
        """Sets the subject configuration for the cycle."""
        self._subjects_data = subjects_data
        return self

    def with_subject_order(self, subject_order: List[str]) -> 'CycleBuilder':
        """Sets a preferred initial order for subjects in the queue."""
        self._subject_order = subject_order
        return self

    def from_existing(self, cycle_id: int) -> 'CycleBuilder':
        """Sets the builder to update an existing cycle."""
        self._cycle_id = cycle_id
        return self

    def build(self) -> int:
        """
        Executes the build process.
        Creates or updates the cycle, processes subjects, and generates the queue.
        Returns the ID of the created or updated cycle.
        """
        if self._cycle_id:
            log.info(f"Builder is updating existing cycle_id: {self._cycle_id}")
            self._update_existing_cycle()
        elif self._exam_id:
            log.info(f"Builder is creating new cycle for exam_id: {self._exam_id}")
            self._create_new_cycle()
        else:
            raise ValueError("CycleBuilder requires either an exam_id (for creation) or a cycle_id (for update).")

        self._process_subjects()
        self._generate_queue()

        log.info(f"Cycle build complete for cycle_id: {self._cycle_id}")
        return self._cycle_id

    def _create_new_cycle(self):
        """Private helper for the creation step."""
        self._cycle_id = self._cycle_service.create(
            self._cycle_data['name'], self._cycle_data['duration'],
            self._cycle_data['is_continuous'], self._cycle_data['daily_goal'],
            self._exam_id,
            self._cycle_data.get('timing_strategy', 'Adaptive')  # Safely get timing strategy
        )

    def _update_existing_cycle(self):
        """Private helper for the update step."""
        self._cycle_service.update_properties(
            self._cycle_id, self._cycle_data['name'], self._cycle_data['duration'],
            self._cycle_data['is_continuous'], self._cycle_data['daily_goal'],
            self._cycle_data.get('is_active', False),  # Safely get is_active, default to False
            self._cycle_data.get('timing_strategy', 'Adaptive')  # Safely get timing strategy
        )
        self._cycle_subject_service.delete_subjects_for_cycle(self._cycle_id)

    def _process_subjects(self):
        """Private helper to add/update subjects and their calculated weights."""
        if self._cycle_id is None: return

        for subject_ui_data in self._subjects_data:
            master_subject = self._master_subject_service.get_master_subject_by_name(subject_ui_data['name'])
            if not master_subject: continue

            weights = {
                "relevance": subject_ui_data['relevance'], "volume": subject_ui_data['volume'],
                "difficulty": subject_ui_data['difficulty'], "is_active": subject_ui_data['is_active']
            }
            final_weight = business_logic.calculate_final_weight(weights['relevance'], weights['volume'],
                                                                 weights['difficulty'])
            num_blocks = business_logic.calculate_num_blocks(final_weight)
            calculated_data = {'final_weight': final_weight, 'num_blocks': num_blocks}

            self._cycle_subject_service.add_subject_to_cycle(self._cycle_id, master_subject.id, weights,
                                                             calculated_data)

    def _generate_queue(self):
        """Private helper to generate and save the study queue."""
        if self._cycle_id is None: return

        all_cycle_subjects = self._cycle_subject_service.get_subjects_for_cycle(self._cycle_id)
        active_cycle_subjects = [cs for cs in all_cycle_subjects if cs.is_active]

        study_queue_ids = []
        if self._subject_order:
            log.info(f"Applying custom subject order to queue generation.")
            subject_map = {cs.name: cs for cs in active_cycle_subjects}

            # Add subjects in the user-defined order first
            ordered_subjects_set = set()
            for subject_name in self._subject_order:
                if subject := subject_map.get(subject_name):
                    study_queue_ids.extend([subject.id] * subject.num_blocks_in_cycle)
                    ordered_subjects_set.add(subject_name)

            # Add the remaining active subjects and randomize them
            remaining_subjects = [cs for cs in active_cycle_subjects if cs.name not in ordered_subjects_set]
            study_queue_ids.extend(business_logic.generate_study_queue(remaining_subjects))
        else:
            # Original behavior
            study_queue_ids = business_logic.generate_study_queue(active_cycle_subjects)

        self._queue_service.save_queue(self._cycle_id, study_queue_ids)