# app/services/study_queue_service.py
import json
import logging
from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.subject import CycleSubject
from app.services.interfaces import IStudyQueueService

log = logging.getLogger(__name__)


class SqliteStudyQueueService(IStudyQueueService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def save_queue(self, cycle_id: int, queue: List[int]):
        conn = self._conn_factory.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_queue WHERE cycle_id = ?", (cycle_id,))
        queue_data = [(cycle_id, cycle_subject_id, order) for order, cycle_subject_id in enumerate(queue)]
        cursor.executemany("INSERT INTO study_queue (cycle_id, cycle_subject_id, queue_order) VALUES (?, ?, ?)",
                         queue_data)
        conn.commit()

    def get_next_in_queue(self, cycle_id: int, position: int) -> Optional[CycleSubject]:
        conn = self._conn_factory.get_connection()
        row = conn.execute(
            "SELECT CS.*, S.name, S.color FROM study_queue AS Q JOIN cycle_subjects AS CS ON Q.cycle_subject_id = CS.id JOIN subjects AS S ON CS.subject_id = S.id WHERE Q.cycle_id = ? AND Q.queue_order = ?",
            (cycle_id, position)).fetchone()
        if not row: return None
        row_dict = dict(row)
        hysteresis_data_str = row_dict.pop('state_hysteresis_data', '{}')
        row_dict['state_hysteresis_data'] = json.loads(hysteresis_data_str) if hysteresis_data_str else {}
        return CycleSubject(**row_dict)