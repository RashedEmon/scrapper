from urllib.parse import quote_plus
import sqlalchemy as sa
from sqlalchemy.engine.url import URL
from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from scrapper import config

Base = declarative_base()

class RedShiftManager:

    def __init__(self) -> None:
        query = {}
        if config.DEBUG:
            query = {
                "sslmode": "disable",
            }
        # Build the sqlalchemy URL
        url = URL.create(
            drivername="postgresql",
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB_NAME, 
            username=config.POSTGRES_USER, 
            password=config.POSTGRES_PASSWORD,
            query=query
        )
        self.engine = sa.create_engine(url)
        self.SessionFactory = sa_orm.sessionmaker()
        self.SessionFactory.configure(bind=self.engine)
        self.session = self.SessionFactory()
        Base.metadata.create_all(bind=self.engine, checkfirst=True)
    
    def get_session(self):
        return self.session

    def get_new_session(self):
        return self.SessionFactory()
    
    def close(self):
        if self.session:
            self.session.close()
