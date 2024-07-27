from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from scrapper import config

Base = declarative_base()

class DatabaseManager:

    def __init__(self) -> None:
        query = {}
        if config.DEBUG:
            query = {
                "ssl": "disable",
            }
        # Build the sqlalchemy URL
        url = URL.create(
            drivername="postgresql+asyncpg",
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB_NAME, 
            username=config.POSTGRES_USER, 
            password=config.POSTGRES_PASSWORD,
            query=query
        )
        self.engine = create_async_engine(url)
        self.SessionFactory = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @property
    def get_session(self):
        return self.SessionFactory
    
    async def dispose(self):
        if self.engine:
            await self.engine.dispose()
    