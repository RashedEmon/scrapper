from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

class DatabaseManager:
    _instance = None
    _engine = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._engine = create_engine('sqlite:///golf_courses.db', echo=True)  # Replace with your database URL
            cls._instance._Session = sessionmaker(bind=cls._instance._engine)
        return cls._instance

    @property
    def session(self):
        return self._Session()

    def close(self):
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._Session = None
            DatabaseManager._instance = None

