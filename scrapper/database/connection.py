from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from scrapy import settings
from urllib.parse import quote_plus
from .models import Base

from scrapper.config import HOST, PORT, USERNAME, PASSWORD, DB_NAME

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
                f'postgresql://{USERNAME}:{quote_plus(PASSWORD)}@'
                f'{HOST}:{PORT}/{DB_NAME}'
            )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine, checkfirst=True)

    def get_session(self):
        """get postgres session"""

        return self.Session()

    @staticmethod
    def close_session(session):
        """close postgres session"""

        if session.is_active:
            session.close()
