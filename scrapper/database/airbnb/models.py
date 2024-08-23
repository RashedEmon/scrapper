from sqlalchemy import Column, func, ForeignKey, VARCHAR, INTEGER, FLOAT, BOOLEAN, JSON, TIMESTAMP, TEXT
from sqlalchemy.orm import relationship

from scrapper.database.connection import Base


class HostsModel(Base):
    __tablename__ = 'host'

    host_id           = Column(VARCHAR(50), primary_key=True)
    host_name         = Column(VARCHAR(50))
    number_of_reviews = Column(INTEGER)
    rating            = Column(FLOAT)
    years_hosting     = Column(INTEGER)
    is_super_host     = Column(BOOLEAN)
    is_verified       = Column(BOOLEAN)
    profile_image     = Column(VARCHAR(500))
    about             = Column(TEXT)
    host_details      = Column(JSON)
    updated_at        = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at        = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class PropertyModel(Base):
    __tablename__ = 'property'

    property_id       = Column(VARCHAR(50), primary_key=True)
    property_name     = Column(VARCHAR(256))
    country           = Column(VARCHAR(50))
    state             = Column(VARCHAR(50))
    city              = Column(VARCHAR(50))
    amenities         = Column(JSON)
    room_arrangement  = Column(JSON)
    rating            = Column(FLOAT)
    detailed_review   = Column(JSON)
    number_of_reviews = Column(INTEGER)
    images            = Column(JSON)
    price             = Column(FLOAT)
    currency_code     = Column(VARCHAR(5))
    facilities        = Column(JSON)
    policies          = Column(JSON)
    host_id           = Column(VARCHAR(50), ForeignKey('host.host_id'))
    latitude          = Column(FLOAT)
    longitude         = Column(FLOAT)
    updated_at        = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at        = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    host = relationship("HostsModel")



class ReviewsModel(Base):
    __tablename__ = 'reviews'

    property_id        = Column(VARCHAR(50), ForeignKey('property.property_id'), nullable=False)
    review_id          = Column(VARCHAR(100), primary_key=True)
    reviewer_name      = Column(VARCHAR(50))
    comments           = Column(TEXT)
    profile_image_url  = Column(VARCHAR(1000))
    review_date        = Column(TIMESTAMP)
    reviewer_location  = Column(VARCHAR(100))
    rating             = Column(FLOAT)
    language           = Column(VARCHAR(length=5))
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    property = relationship("PropertyModel")


class RequestTracker(Base):

    __tablename__ = 'request_tracker'

    url                = Column(VARCHAR(5000), nullable=False, primary_key=True)
    referer            = Column(VARCHAR(5000))
    status_code        = Column(INTEGER)
    method             = Column(VARCHAR(50))
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class PropertyUrls(Base):

    __tablename__ = 'property_urls'

    url                = Column(VARCHAR(5000), nullable=False, primary_key=True)
    referer            = Column(VARCHAR(1000))
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class AirbnbUrls(Base):

    __tablename__ = 'airbnb_urls'

    url                = Column(VARCHAR(5000), nullable=False, primary_key=True)
    referer            = Column(VARCHAR(1000))
    is_visited         = Column(BOOLEAN, default=False, nullable=False)
    is_taken         = Column(BOOLEAN, default=False, nullable=False)
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)