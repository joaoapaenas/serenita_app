# app/services/cycle_subject_service.py
import json
import logging
from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.subject import CycleSubject
from app.services import BaseService
from app.services.interfaces import ICycleSubjectService

log = logging.getLogger(__name__)


class SqliteCycleSubjectService(BaseService, ICycleSubjectService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def add_subject_to_cycle(
        self, cycle_id: int, subject_id: int, weights: dict, calculated_data: dict
    ):
        from datetime import date

        today_str = date.today().isoformat()
        self._execute_query(
            "INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight, is_active, final_weight_calc, num_blocks_in_cycle, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                cycle_id,
                subject_id,
                weights["relevance"],
                weights["volume"],
                weights["difficulty"],
                weights["is_active"],
                calculated_data["final_weight"],
                calculated_data["num_blocks"],
                today_str,
            ),
        )

    def get_subjects_for_cycle(self, cycle_id: int) -> List[CycleSubject]:
        rows = self._execute_query(
            "SELECT CS.id, CS.cycle_id, CS.subject_id, CS.relevance_weight, CS.volume_weight, CS.difficulty_weight, CS.is_active, CS.final_weight_calc, CS.num_blocks_in_cycle, CS.date_added, CS.current_strategic_state, CS.state_hysteresis_data, S.name, S.color FROM cycle_subjects AS CS JOIN subjects AS S ON CS.subject_id = S.id WHERE CS.cycle_id = ?",
            (cycle_id,),
        ).fetchall()
        cycle_subjects = []
        for row in rows:
            # Create a mutable dictionary from row for manipulation
            data = dict(row)
            hysteresis_data_str = data.pop("state_hysteresis_data", "{}")
            data["state_hysteresis_data"] = (
                json.loads(hysteresis_data_str) if hysteresis_data_str else {}
            )
            cycle_subjects.append(
                CycleSubject(
                    id=data["id"],
                    cycle_id=data["cycle_id"],
                    subject_id=data["subject_id"],
                    relevance_weight=data["relevance_weight"],
                    volume_weight=data["volume_weight"],
                    difficulty_weight=data["difficulty_weight"],
                    is_active=data["is_active"],
                    final_weight_calc=data["final_weight_calc"],
                    num_blocks_in_cycle=data["num_blocks_in_cycle"],
                    name=data["name"],
                    color=data["color"],
                    date_added=data["date_added"],
                    current_strategic_state=data["current_strategic_state"],
                    state_hysteresis_data=data["state_hysteresis_data"],
                    work_units=[],  # Initialize as empty list
                )
            )
        return cycle_subjects

    def get_cycle_subject(self, cycle_subject_id: int) -> Optional[CycleSubject]:
        row = self._execute_query(
            "SELECT CS.id, CS.cycle_id, CS.subject_id, CS.relevance_weight, CS.volume_weight, CS.difficulty_weight, CS.is_active, CS.final_weight_calc, CS.num_blocks_in_cycle, CS.date_added, CS.current_strategic_state, CS.state_hysteresis_data, S.name, S.color FROM cycle_subjects AS CS JOIN subjects AS S ON CS.subject_id = S.id WHERE CS.id = ?",
            (cycle_subject_id,),
        ).fetchone()
        if not row:
            return None
        # Create a mutable dictionary from row for manipulation
        data = dict(row)
        hysteresis_data_str = data.pop("state_hysteresis_data", "{}")
        data["state_hysteresis_data"] = (
            json.loads(hysteresis_data_str) if hysteresis_data_str else {}
        )
        return CycleSubject(
            id=data["id"],
            cycle_id=data["cycle_id"],
            subject_id=data["subject_id"],
            relevance_weight=data["relevance_weight"],
            volume_weight=data["volume_weight"],
            difficulty_weight=data["difficulty_weight"],
            is_active=data["is_active"],
            final_weight_calc=data["final_weight_calc"],
            num_blocks_in_cycle=data["num_blocks_in_cycle"],
            name=data["name"],
            color=data["color"],
            date_added=data["date_added"],
            current_strategic_state=data["current_strategic_state"],
            state_hysteresis_data=data["state_hysteresis_data"],
            work_units=[],  # Initialize as empty list
        )

    def delete_subjects_for_cycle(self, cycle_id: int):
        self._execute_query("DELETE FROM cycle_subjects WHERE cycle_id = ?", (cycle_id,))

    def update_cycle_subject_difficulty(
        self, cycle_subject_id: int, new_difficulty: int
    ):
        self._execute_query(
            "UPDATE cycle_subjects SET difficulty_weight = ? WHERE id = ?",
            (new_difficulty, cycle_subject_id),
        )

    def update_cycle_subject_calculated_fields(
        self, cycle_subject_id: int, final_weight: float, num_blocks: int
    ):
        self._execute_query(
            "UPDATE cycle_subjects SET final_weight_calc = ?, num_blocks_in_cycle = ? WHERE id = ?",
            (final_weight, num_blocks, cycle_subject_id),
        )

    def update_cycle_subject_state(
        self, cycle_subject_id: int, state: str, hysteresis_data: dict
    ):
        hysteresis_data_str = json.dumps(hysteresis_data)
        self._execute_query(
            "UPDATE cycle_subjects SET current_strategic_state = ?, state_hysteresis_data = ? WHERE id = ?",
            (state, hysteresis_data_str, cycle_subject_id),
        )
