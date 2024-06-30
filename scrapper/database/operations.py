from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from connection import DatabaseManager


class CommonDBOperation:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def insert_or_ignore(self, model_class, data_dict):
        session = self.db_manager.session
        try:
            instance = model_class(**data_dict)
            session.add(instance)
            session.commit()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()

# Example usage:
# db_operations = CommonDBOperation()
# data_dict = {'CourseName': 'Sample Course', 'City': 'Sample City', ...}
# db_operations.insert_or_ignore(GolfCourse, data_dict)
# DatabaseManager().close()
