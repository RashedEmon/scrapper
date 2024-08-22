from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, String

from scrapper.database.connection import DatabaseManager
from scrapper.database.airbnb.models import RequestTracker, PropertyUrls

class DBOperations:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def get_incomplete_xmls_from_request_tracker(self):
        async with self.db_manager.get_session() as session:
            async with session.begin():
                try:
                    query = (
                        select(RequestTracker.referer, func.count(RequestTracker.referer))
                        .group_by(RequestTracker.referer)
                        .having(func.count(RequestTracker.referer) < 50000)
                    )

                    result = await session.execute(query)
                    return result.all()
                except Exception as err:
                    print("got error in get_incomplete_xmls_from_request_tracker => ", err)

    async def get_missing_urls(self, property_urls: PropertyUrls, request_tracker: RequestTracker):
        urls = []
        try:
            async with self.db_manager.get_session() as session:
                async with session.begin():
                    query = select(PropertyUrls.url).outerjoin(
                        RequestTracker, 
                        PropertyUrls.url == RequestTracker.url
                    ).where(
                        or_(
                            RequestTracker.url == None,
                            (RequestTracker.status_code != 200) & (RequestTracker.status_code != 410)
                        )
                    )
                    result = await session.execute(query)
                    urls = result.scalars().all()
        except Exception as err:
            print(err)
        
        return urls
