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
                "ssl": "false",
            }
        # Build the sqlalchemy URL
        url = URL.create(
            drivername="redshift+redshift_connector",
            host=config.REDSHIFT_HOST,
            port=config.REDSHIFT_PORT,
            database=config.REDSHIFT_DB_NAME, 
            username=config.REDSHIFT_USER, 
            password=config.REDSHIFT_PASSWORD,
            query=query
        )
        self.engine = sa.create_engine(url)
        self.SessionFactory = sa_orm.sessionmaker()
        self.SessionFactory.configure(bind=self.engine)
        self.session = self.SessionFactory()
        metadata = sa.MetaData(bind=self.session.bind)
        Base.metadata.create_all(bind=self.engine, checkfirst=True)
    
    def get_session(self):
        return self.session

    def get_new_session(self):
        return self.SessionFactory()
    
    def close(self):
        if self.session:
            self.session.close()
