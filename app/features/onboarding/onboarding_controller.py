# app/features/onboarding/onboarding_controller.py

import logging
from collections import defaultdict

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QMessageBox

from app.core import business_logic
from app.core.topic_parser import parse_edital_topics
from app.models.exam import Exam
from app.models.subject import CycleSubject, Subject
from app.services.interfaces import (IExamService, ICycleService, IMasterSubjectService,
                                     ITemplateSubjectService, ICycleSubjectService, IStudyQueueService,
                                     IWorkUnitService)
from .components.define_exam_page import DefineExamPage
from .components.goal_page import GoalPage
from .components.import_topics_page import ImportTopicsPage
from .components.subjects_config_page import SubjectsConfigPage
from .onboarding_flow_manager import OnboardingFlowManager
from .onboarding_result_processor import OnboardingResultProcessor
from .onboarding_view import OnboardingView

log = logging.getLogger(__name__)


class OnboardingController(QObject):
    onboarding_complete = Signal()
    onboarding_cancelled = Signal()

    def __init__(self, view: OnboardingView, user_id: int, exam_service: IExamService,
                 master_subject_service: IMasterSubjectService, template_subject_service: ITemplateSubjectService,
                 cycle_service: ICycleService, cycle_subject_service: ICycleSubjectService,
                 study_queue_service: IStudyQueueService, work_unit_service: IWorkUnitService):
        super().__init__(None)
        self._view = view
        self.exam_service = exam_service
        self.master_subject_service = master_subject_service
        self.template_subject_service = template_subject_service
        self.work_unit_service = work_unit_service

        self.result_processor = OnboardingResultProcessor(
            user_id=user_id,
            exam_service=self.exam_service,
            work_unit_service=self.work_unit_service,
            cycle_service=cycle_service,
            cycle_subject_service=cycle_subject_service,
            master_subject_service=self.master_subject_service,
            study_queue_service=study_queue_service
        )

        # --- State Data ---
        self.final_exam_data = {}
        self.imported_topics = defaultdict(list)
        self.subjects_config_cache = []

        # --- Create ALL possible pages upfront. They will be hidden/shown as needed. ---
        self.pages = {
            "goal": self._view.create_page_goal(self.exam_service.get_available_templates()),
            "define_exam": self._view.create_page_define_exam(),
            "subjects_config": self._view.create_page_subjects_config(),
            "import_topics": self._view.create_page_import_topics(),
            "cycle_settings": self._view.create_page_cycle_settings()
        }

        self.flow_manager = OnboardingFlowManager(self.pages)

        self._connect_view_signals()


    @property
    def current_page_index(self) -> int:
        return self.flow_manager.current_page_index

    @current_page_index.setter
    def current_page_index(self, value: int):
        self.flow_manager.current_page_index = value

    def start(self):
        for page in self.pages.values():
            self._view.add_page(page)
        self._view.go_to_page(self.flow_manager.current_page())
        self._view.update_navigation(
            self.current_page_index, self.flow_manager.total_pages(), self.flow_manager.can_proceed()
        )

    def _connect_view_signals(self):
        self.pages["goal"].goal_selected.connect(self._on_goal_selection_changed)
        self.pages["import_topics"].process_topics_requested.connect(self._on_process_topics)
        self.pages["import_topics"].topics_changed.connect(self._on_topics_changed)
        self.pages["subjects_config"].master_subject_add_requested.connect(self._on_add_master_subject)
        self._view.next_step_requested.connect(self._on_next_step)
        self._view.back_step_requested.connect(self._on_back_step)
        self._view.finish_requested.connect(self._on_finish)
        self._view.cancel_requested.connect(self.onboarding_cancelled.emit)

    def _on_add_master_subject(self, name: str):
        """Handles the request to create a new master subject from the UI."""
        log.info(f"Onboarding: Attempting to add new master subject: '{name}'")
        new_id = self.master_subject_service.add_master_subject(name)
        if new_id:
            log.info(f"Successfully added master subject '{name}' with new ID: {new_id}")
            # Create a model instance for the new subject.
            new_subject_model = Subject(
                id=new_id, name=name, color=None, created_at="",
                updated_at="", soft_delete=False, deleted_at=None
            )
            # Get the presenter for the subjects page and tell it to update the view.
            subjects_page = self.pages["subjects_config"]
            subjects_page.presenter.add_new_master_subject(new_subject_model, check_item=True)
        else:
            log.warning(f"Failed to add master subject '{name}'. It likely already exists.")
            QMessageBox.warning(self._view, "Duplicate Subject", f"The subject '{name}' already exists.")

    def _on_goal_selection_changed(self, selection):
        goal_page = self.pages["goal"]
        if isinstance(selection, Exam):
            subjects = self.template_subject_service.get_subjects_for_template(selection.id)
            goal_page.update_details(selection, subjects)
        else:
            goal_page.update_details(None, None)

        selection_key = "none"
        if isinstance(selection, Exam):
            selection_key = selection.id
        elif isinstance(selection, str):
            selection_key = selection

        self.flow_manager.set_flow_for_selection(selection_key)
        self._view.update_navigation(
            self.current_page_index, self.flow_manager.total_pages(), self.flow_manager.can_proceed()
        )

    def _on_next_step(self):
        current_page = self.flow_manager.current_page()
        self._prepare_next_page(current_page)

        if next_page := self.flow_manager.next_page():
            self._view.go_to_page(next_page)
            self._view.update_navigation(
                self.current_page_index, self.flow_manager.total_pages(), self.flow_manager.can_proceed()
            )

    def _on_back_step(self):
        if previous_page := self.flow_manager.previous_page():
            self._view.go_to_page(previous_page)
            self._view.update_navigation(
                self.current_page_index, self.flow_manager.total_pages(), self.flow_manager.can_proceed()
            )

    def _prepare_next_page(self, current_page_widget: QWidget):
        """Contains the logic to populate the upcoming page with necessary data."""
        if isinstance(current_page_widget, (GoalPage, DefineExamPage)):
            self._populate_subjects_config_page()

        elif isinstance(current_page_widget, SubjectsConfigPage):
            self.subjects_config_cache = current_page_widget.get_data()
            next_page = self.pages["import_topics"]
            active_subjects = [s['name'] for s in self.subjects_config_cache if s['is_active']]
            next_page.populate_subjects_combo(active_subjects)

        elif isinstance(current_page_widget, ImportTopicsPage):
            next_page = self.pages["cycle_settings"]
            active_subjects_with_weights = []
            for sc in self.subjects_config_cache:
                if sc['is_active']:
                    weight = business_logic.calculate_final_weight(sc['relevance'], sc['volume'], sc['difficulty'])
                    active_subjects_with_weights.append({'name': sc['name'], 'weight': weight})
            active_subjects_with_weights.sort(key=lambda x: x['weight'], reverse=True)
            next_page.populate_subject_order_list(active_subjects_with_weights)

    def _populate_subjects_config_page(self):
        subjects_page = self.pages["subjects_config"]
        presenter = subjects_page.presenter
        all_master_subjects = self.master_subject_service.get_all_master_subjects()
        presenter.load_master_subjects(all_master_subjects)

        selection = self.pages["goal"].get_selection()
        if isinstance(selection, Exam):
            template_subjects = self.template_subject_service.get_subjects_for_template(selection.id)
            subjects_in_cycle = [
                CycleSubject(
                    id=0, cycle_id=0, subject_id=self.master_subject_service.get_master_subject_by_name(sub_data['name']).id,
                    name=sub_data['name'], relevance_weight=sub_data['relevance_weight'],
                    volume_weight=sub_data['volume_weight'], difficulty_weight=3, is_active=True,
                    final_weight_calc=0, num_blocks_in_cycle=0
                ) for sub_data in template_subjects if self.master_subject_service.get_master_subject_by_name(sub_data['name'])
            ]
            presenter.populate_for_editing(subjects_in_cycle)

    def _on_process_topics(self, subject_name: str, pasted_text: str):
        topics_page = self.pages["import_topics"]
        parsed = parse_edital_topics(pasted_text)
        existing_topics = set(self.imported_topics.get(subject_name, []))
        new_topic_list = self.imported_topics.get(subject_name, [])
        for topic in parsed:
            if topic not in existing_topics:
                new_topic_list.append(topic)
                existing_topics.add(topic)
        self.imported_topics[subject_name] = new_topic_list
        topics_page.update_imported_topics_preview(self.imported_topics)
        log.info(f"Processed and added {len(parsed)} topics for subject '{subject_name}'.")
        topics_page.clear_paste_area()

    def _on_finish(self):
        selection = self.pages["goal"].get_selection()
        if isinstance(selection, str) and selection == "custom":
            self.final_exam_data = self.pages["define_exam"].get_data()
        elif isinstance(selection, Exam):
            template_exam = selection
            self.final_exam_data.update({
                'name': template_exam.name.replace(" (Template)", ""),
                'institution': template_exam.institution, 'role': template_exam.role,
                'area': template_exam.area, 'exam_board': template_exam.exam_board,
                'predicted_exam_date': template_exam.predicted_exam_date
            })
        else:
            log.warning("Finish button clicked with no valid selection.")
            return

        self.result_processor.process_and_create(
            final_exam_data=self.final_exam_data,
            imported_topics=self.imported_topics,
            final_subjects_config=self.subjects_config_cache,
            final_subject_order=self.pages["cycle_settings"].get_subject_order(),
            final_daily_goal=self.pages["cycle_settings"].get_daily_goal()
        )
        self.onboarding_complete.emit()

    def _on_topics_changed(self, new_topic_data: dict):
        self.imported_topics = defaultdict(list, new_topic_data)