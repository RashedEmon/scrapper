from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, String
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

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

    async def get_missing_urls(self, property_urls: PropertyUrls, request_tracker: RequestTracker, limit=None, offset=None):
        result_list = []
        try:
            async with self.db_manager.get_session() as session:
                async with session.begin():
                    query = select(PropertyUrls.url, PropertyUrls.referer).outerjoin(
                        RequestTracker, 
                        PropertyUrls.url == RequestTracker.url
                    ).where(
                        or_(
                            RequestTracker.url == None,
                            (RequestTracker.status_code != 200) & (RequestTracker.status_code != 410)
                        )
                    ).distinct()
                    if limit:
                        query = query.limit(limit)
                    
                    if offset:
                        query = query.offset(offset)

                    result = await session.execute(query)
                    column_names = result.keys()
                    for row in result.fetchall():
                        row_dict = dict(zip(column_names, row))
                        result_list.append(row_dict)
        except Exception as err:
            print(err)
        
        return result_list
    
    async def get_missing_urls_count(self, property_urls: PropertyUrls, request_tracker: RequestTracker):
        
        try:
            async with self.db_manager.get_session() as session:
                async with session.begin():
                    query = select(func.count(func.distinct(PropertyUrls.url))).outerjoin(
                        RequestTracker, 
                        PropertyUrls.url == RequestTracker.url
                    ).where(
                        or_(
                            RequestTracker.url == None,
                            (RequestTracker.status_code != 200) & (RequestTracker.status_code != 410)
                        )
                    )
                    print(str(query))
                    result = await session.execute(query)
                    result = result.scalars().all()
                    if len(result) >= 1:
                        return result[0]
        except Exception as err:
            print(err)
    

    async def bulk_insert_data(self, Model, data_list, batch_size=1000):
        total_inserted = 0
        async with self.db_manager.get_session() as session:
            async with session.begin():
                try:
                    for i in range(0, len(data_list), batch_size):
                        batch = data_list[i:i+batch_size]
                        try:
                            stmt = insert(Model).values(batch)
                            stmt = stmt.on_conflict_do_nothing()
                            result = await session.execute(stmt)
                            total_inserted += result.rowcount
                        except IntegrityError:
                            for item in batch:
                                try:
                                    stmt = insert(Model).values(**item)
                                    stmt = stmt.on_conflict_do_nothing()
                                    result = await session.execute(stmt)
                                    if result.rowcount > 0:
                                        total_inserted += 1
                                except IntegrityError:
                                    pass
                        
                        await session.commit()

                except SQLAlchemyError as e:
                    await session.rollback()
                    print(f"An error occurred: {str(e)}")
                except Exception as err:
                    print("error occured in bulk_insert_data=>", err)

        return total_inserted
