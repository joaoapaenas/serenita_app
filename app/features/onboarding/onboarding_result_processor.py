# app/features/onboarding/onboarding_result_processor.py
import logging
from collections import defaultdict

from app.core.builders import CycleBuilder
from app.services.interfaces import (IExamService, IWorkUnitService, ICycleService,
                                     ICycleSubjectService, IMasterSubjectService, IStudyQueueService)

log = logging.getLogger(__name__)


class OnboardingResultProcessor:
    """
    Handles the final step of the onboarding process: taking all the gathered
    data and creating the necessary database entities (Exam, Cycle, etc.).
    """

    def __init__(self, user_id: int, exam_service: IExamService, work_unit_service: IWorkUnitService,
                 cycle_service: ICycleService, cycle_subject_service: ICycleSubjectService,
                 master_subject_service: IMasterSubjectService, study_queue_service: IStudyQueueService):
        self.user_id = user_id
        self.exam_service = exam_service
        self.work_unit_service = work_unit_service
        self.cycle_service = cycle_service
        self.cycle_subject_service = cycle_subject_service
        self.master_subject_service = master_subject_service
        self.study_queue_service = study_queue_service

    def process_and_create(self, final_exam_data: dict, imported_topics: defaultdict,
                           final_subjects_config: list, final_subject_order: list, final_daily_goal: int):
        """
        Executes the creation of the exam, subjects, topics, and cycle.
        """
        log.info(f"Creating new exam '{final_exam_data.get('name')}'.")
        new_exam_id = self.exam_service.create(user_id=self.user_id, **final_exam_data)
        if not new_exam_id:
            log.error("Failed to create a new exam during onboarding. Aborting.")
            return

        log.info(f"New exam created with ID: {new_exam_id}")

        for subject_name, topics in imported_topics.items():
            master_sub = self.master_subject_service.get_master_subject_by_name(subject_name)
            if master_sub and topics:
                self.work_unit_service.add_topics_bulk(master_sub.id, topics)

        cycle_properties = {
            'name': f"Prep for {final_exam_data.get('name', 'Exam')}",
            'duration': 60,
            'is_continuous': True,
            'daily_goal': final_daily_goal
        }

        # The builder handles setting the new cycle as active
        (CycleBuilder(self.cycle_service, self.cycle_subject_service, self.master_subject_service, self.study_queue_service)
         .for_exam(new_exam_id)
         .with_properties(cycle_properties)
         .with_subjects(final_subjects_config)
         .with_subject_order(final_subject_order)
         .build())

        log.info("Onboarding result processing complete. Exam and Cycle created.")