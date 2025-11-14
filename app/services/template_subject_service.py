# app/services/template_subject_service.py
import logging
from typing import List

from app.core.database import IDatabaseConnectionFactory
from app.services import BaseService
from app.services.interfaces import ITemplateSubjectService

log = logging.getLogger(__name__)


class SqliteTemplateSubjectService(BaseService, ITemplateSubjectService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def get_subjects_for_template(self, exam_id: int) -> List[dict]:
        rows = self._execute_query(
            "SELECT S.name, TS.relevance_weight, TS.volume_weight FROM template_subjects AS TS JOIN subjects AS S ON TS.subject_id = S.id WHERE TS.exam_id = ?",
            (exam_id,)).fetchall()
        return [dict(row) for row in rows]