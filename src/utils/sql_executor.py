from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import StatementError
from asyncpg.exceptions import QueryCanceledError
from fastapi import HTTPException
from config import settings


class SQLExecutor:
    def __init__(self):
        self.engine = create_async_engine(
            settings.GAME_DATABASE_URL,
            isolation_level="AUTOCOMMIT"
        )

    async def execute_sql(self, sql_query: str) -> dict:
        sql_query = sql_query.rstrip(';').strip()
        self._validate_sql(sql_query)
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SET statement_timeout TO 5000"))
                result = await conn.execute(text(sql_query))
                if result.returns_rows:
                    columns = list(result.keys())
                    data = []
                    for row in result.fetchall():
                        processed_row = []
                        for value in row:
                            if isinstance(value, (date, datetime)):
                                processed_row.append(value.isoformat())
                            else:
                                processed_row.append(value)
                        data.append(processed_row)
                    return {
                        "columns": columns,
                        "data": data,
                        "row_count": len(data)
                    }
                return {
                    "columns": [],
                    "data": [],
                    "row_count": result.rowcount
                }
        except QueryCanceledError:
            raise HTTPException(status_code=400,
                                detail="Время выполнения запроса превышено")
        except StatementError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка выполнения: {str(e.orig)}"
            )

    def _validate_sql(self, sql_query: str):
        """Базовая проверка SQL-запроса на безопасность"""
        sql_lower = sql_query.lower()
        forbidden_keywords = [
                                'insert', 'delete', 'update', 'grant',
                                'revoke', 'create', 'alter', 'drop',
                                'truncate', '/*', '*/', 'pg_', 'user'
                            ]
        for keyword in forbidden_keywords:
            if keyword in sql_lower:
                raise HTTPException(
                    status_code=400,
                    detail="Запрещенная операция в SQL-запросе"
                )
