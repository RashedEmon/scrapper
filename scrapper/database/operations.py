from typing import Any, List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import insert, select, and_

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy import inspect

from .connection import RedShiftManager


class CommonDBOperation:
    def __init__(self):
        self.db_manager = RedShiftManager()

    def insert_or_ignore(self, model_class, data_dict):
        session = self.db_manager.get_session()
        try:
            instance = model_class(**data_dict)
            session.add(instance)
            session.commit()
        except IntegrityError:
            session.rollback()

    def insert_or_update(self, model_class, data_dict: dict):
        session = self.db_manager.get_session()

        primary_keys = [key.name for key in model_class.__table__.primary_key]
        pk_values = {pk: data_dict.get(pk) for pk in primary_keys}
        
        if not all(pk_values.values()):
            raise ValueError("All primary key values must be provided")
    
        try:
            existing_record = session.query(model_class).filter_by(**pk_values).one()
            
            for key, value in data_dict.items():
                setattr(existing_record, key, value)
            
            session.commit()
            return existing_record, False
        
        except NoResultFound:
            new_record = model_class(**data_dict)
            session.add(new_record)
            
            try:
                session.commit()
                return new_record, True
            except IntegrityError:
                session.rollback()
                raise ValueError("Unable to insert new record due to integrity error")
        finally:
            self.check_and_expunge(session, model_class(**data_dict))
    
    def upsert_rows(self, model, data: list[dict], unique_columns: list[str]):
        res = False
        session = self.db_manager.get_session()
        table = model.__table__
        
        try:
            for row in data:
                where_clause = and_(*[getattr(table.c, col) == row[col] for col in unique_columns])

                exists_stmt = select(table).where(where_clause)
                existing_row = session.execute(exists_stmt).first()

                if existing_row:
                    update_values = {k: v for k, v in row.items() if k not in unique_columns}
                    update_stmt = table.update().where(where_clause).values(update_values)
                    session.execute(update_stmt)
                else:
                    insert_stmt = insert(table).values(row)
                    session.execute(insert_stmt)

            session.commit()
            res = True
        except IntegrityError as e:
            session.rollback()
        except Exception as e:
            session.rollback()
        finally:
            self.check_and_expunge(session, [model(**row) for row in data])

        return res
    

    def is_exist(self, model_name, query_filter: list, columns: list):
        session = self.db_manager.get_session()
        try:
            if columns:
                return True if len(session.query(*columns).filter(*query_filter).all()) > 0 else False
            else:
                return True if len(session.query(model_name).filter(*query_filter).all()) > 0 else False
        except Exception as error:
            print(f"Error => get_data_from_db: {error}")

    def close(self):
        self.db_manager.close()

    
    def check_and_expunge(self, session: Session, item: List | Any):
        
        if not isinstance(item, list):
            item = [item]

        for obj in item:
            try:
                mapper = inspect(obj).mapper
                
                pk = tuple(mapper.primary_key_from_instance(obj))

                if mapper.identity_key_from_primary_key(pk) in session.identity_map:
                    print(f"Object {obj} found in identity map. Expunging...")
                    session.expunge(obj)
                    return True
                else:
                    print(f"Object {obj} not found in identity map.")
                    return False
                
            except Exception as err:
                print(err)