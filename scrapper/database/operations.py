from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import exists

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

    def insert_or_update(self, model_class, data_dict):
        primary_keys = [key.name for key in model_class.__table__.primary_key]
        pk_values = {pk: data_dict.get(pk) for pk in primary_keys}
        
        if not all(pk_values.values()):
            raise ValueError("All primary key values must be provided")
    
        try:
            existing_record = self.session.query(model_class).filter_by(**pk_values).one()
            
            for key, value in data_dict.items():
                setattr(existing_record, key, value)
            
            self.session.commit()
            return existing_record, False
        
        except NoResultFound:
            new_record = model_class(**data_dict)
            self.session.add(new_record)
            
            try:
                self.session.commit()
                return new_record, True
            except IntegrityError:
                self.session.rollback()
                raise ValueError("Unable to insert new record due to integrity error")
    
    def upsert_rows(self, model, data: list[dict], unique_columns: list[str]):
        res = False
        session = self.db_manager.get_session()
        table = model.__table__

        # Create the insert statement
        stmt = insert(table).values(data)

        # Add ON CONFLICT clause for upsert behavior
        update_dict = {c.name: c for c in stmt.excluded if c.name not in unique_columns}
        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_dict
        )

        try:
            session.execute(stmt)
            session.commit()
            res = True
        except IntegrityError as e:
            session.rollback()
        except Exception as e:
            session.rollback()
        
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