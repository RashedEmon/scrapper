from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

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
