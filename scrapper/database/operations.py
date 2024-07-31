import logging
from typing import Any, List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import insert, select, and_, func

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import OperationalError, InternalError, InterfaceError, SQLAlchemyError

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .connection import DatabaseManager


class RetriesCompeleted(Exception):
    pass

def on_retry_completed(retry_state):
    if retry_state.outcome.failed:
        raise RetriesCompeleted("All retry attempts have been exhausted.")

class CommonDBOperation:
    def __init__(self):
        self.db_manager = DatabaseManager()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(30), 
        retry=retry_if_exception_type((OperationalError, InternalError, InterfaceError)),
        retry_error_callback=on_retry_completed
    )
    async def insert_or_ignore_async(self, model_class, data_dict):
        async with self.db_manager.get_session() as session:
            async with session.begin():
                try:
                    instance = model_class(**data_dict)
                    session.add(instance)
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(30),
        retry=retry_if_exception_type((OperationalError, InternalError, InterfaceError)),
        retry_error_callback=on_retry_completed
    )
    async def insert_or_update_async(self, model_class, data_dict: dict):
        
        async with self.db_manager.get_session() as session:
            primary_keys = [key.name for key in model_class.__table__.primary_key]
            pk_values = {pk: data_dict.get(pk) for pk in primary_keys}
            
            if not all(pk_values.values()):
                raise ValueError("All primary key values must be provided")
        
            try:
                result = await session.execute(select(model_class).filter_by(**pk_values))
                existing_record = result.scalar_one()
                
                for key, value in data_dict.items():
                    setattr(existing_record, key, value)
                
                await session.commit()
                return existing_record, False
            
            except NoResultFound:
                new_record = model_class(**data_dict)
                session.add(new_record)
                
                try:
                    await session.commit()
                    return new_record, True
                except IntegrityError:
                    await session.rollback()
                    raise ValueError("Unable to insert new record due to integrity error")
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(30),
        retry=retry_if_exception_type((OperationalError, InternalError, InterfaceError)),
        retry_error_callback=on_retry_completed
    )
    async def upsert_rows_async(self, model, data: list[dict], unique_columns: list[str]):
        res = False
        async with self.db_manager.get_session() as session:
            async with session.begin():
                table = model.__table__
                
                try:
                    for row in data:
                        where_clause = and_(*[getattr(table.c, col) == row[col] for col in unique_columns])

                        exists_stmt = select(table).where(where_clause)
                        existing_row = await session.execute(exists_stmt)

                        if existing_row:
                            update_values = {k: v for k, v in row.items() if k not in unique_columns}
                            update_stmt = table.update().where(where_clause).values(update_values)
                            await session.execute(update_stmt)
                        else:
                            insert_stmt = insert(table).values(row)
                            await session.execute(insert_stmt)

                    await session.commit()
                    res = True
                except IntegrityError as e:
                    await session.rollback()
                except Exception as e:
                    await session.rollback()

        return res

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(30),
        retry=retry_if_exception_type((OperationalError, InternalError, InterfaceError)),
        retry_error_callback=on_retry_completed
    )
    async def is_exist_async(self, model_name, query_filter: list, columns: list):
        async with self.db_manager.get_session() as session:
            if columns:
                result = await session.execute(select(func.count()).select_from(select(*columns).filter(*query_filter).subquery()))
                exists = result.scalar() > 0
                return True if exists else False
            else:
                result = await session.execute(select(func.count()).select_from(select(model_name).filter(*query_filter).subquery()))
                exists = result.scalar() > 0
                return True if exists else False
