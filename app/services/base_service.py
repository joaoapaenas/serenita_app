from typing import List, Type, TypeVar, Optional
from app.core.database import IDatabaseConnectionFactory

T = TypeVar('T') # Generic type for our models

class BaseService:
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def _map_row_to_model(self, row, model: Type[T]) -> Optional[T]:
        return model(**dict(row)) if row else None

    def _map_rows_to_model_list(self, rows, model: Type[T]) -> List[T]:
        return [model(**dict(row)) for row in rows]

    def _execute_query(self, query: str, params: tuple = ()):
        with self._conn_factory.get_connection() as conn:
            return conn.execute(query, params)