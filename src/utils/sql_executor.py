from datetime import datetime, date
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
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
            raise HTTPException(status_code=400, detail="Query timeout exceeded")
        except StatementError as e:
            raise HTTPException(
                status_code=400,
                detail=f"SQL execution error: {str(e.orig)}"
            )
    def _validate_sql(self, sql_query: str):
        """Базовая проверка SQL-запроса на безопасность"""
        sql_lower = sql_query.lower()
        
        forbidden_keywords = ['insert', 'delete', 'update', 'grant',
                              'revoke', 'create', 'alter', 'drop', 
                              'truncate', '/*', '*/', 'union']
        for keyword in forbidden_keywords:
            if keyword in sql_lower:
                raise HTTPException(
                    status_code=400,
                    detail=f"Запрещенная операция в SQL-запросе {keyword}"
                )

# более сложная проверка
# async def validate_results(self, user_result: Dict, expected_result: Dict) -> bool:
#     """Расширенная проверка результатов"""
#     # Проверка количества столбцов
#     if len(user_result["columns"]) != len(expected_result.get("columns", [])):
#         return False
    
#     # Проверка имен столбцов (без учета порядка)
#     if set(user_result["columns"]) != set(expected_result.get("columns", [])):
#         return False
    
#     # Преобразуем данные в множество для сравнения без учета порядка строк
#     user_data = {tuple(row) for row in user_result["data"]}
#     expected_data = {tuple(row) for row in expected_result.get("data", [])}
    
#     return user_data == expected_data