from typing import List, Optional, Type, TypeVar, Union
import sqlite3 # Import sqlite3 to check connection type
from sqlalchemy import Connection # Import Connection to check type
from sqlalchemy.sql import text # Import text to wrap query

from app.core.database import IDatabaseConnectionFactory

T = TypeVar("T")  # Generic type for our models


class BaseService:
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def _map_row_to_model(self, row, model: Type[T]) -> Optional[T]:
        return model(**dict(row)) if row else None

    def _map_rows_to_model_list(self, rows, model: Type[T]) -> List[T]:
        return [model(**dict(row)) for row in rows]

    def _execute_query(self, query: str, params: Union[tuple, dict] = ()):
        with self._conn_factory.get_connection() as conn:
            # Check if the connection is a SQLAlchemy Connection
            if isinstance(conn, Connection):
                return conn.execute(text(query), params).mappings()
            else:
                return conn.execute(query, params)

    def _executemany_query(self, query: str, params: List[tuple]):
        with self._conn_factory.get_connection() as conn:
            # Check if the connection is a SQLAlchemy Connection
            if isinstance(conn, Connection):
                return conn.executemany(text(query), params).mappings()
            else:
                return conn.executemany(query, params)
