from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_redshift.dialect import SUPER, VARCHAR, INTEGER, REAL, TIMESTAMP, DOUBLE_PRECISION, SMALLINT, BOOLEAN
from sqlalchemy.orm import relationship

Base = declarative_base()

class PropertyModel(Base):
    __tablename__ = 'property'

    property_id       = Column(VARCHAR(50), primary_key=True)
    property_name     = Column(VARCHAR(256))
    country           = Column(VARCHAR(50))
    state             = Column(VARCHAR(50))
    city              = Column(VARCHAR(50))
    amenities         = Column(SUPER)
    room_arrangement  = Column(SUPER)
    rating            = Column(REAL)
    detailed_review   = Column(SUPER)
    number_of_reviews = Column(INTEGER)
    images            = Column(SUPER)
    price             = Column(REAL)
    currency_code     = Column(VARCHAR(5))
    facilities        = Column(SUPER)
    policies          = Column(SUPER)
    host_id           = Column(VARCHAR(50), ForeignKey('host.host_id'))
    latitude          = Column(DOUBLE_PRECISION)
    longitude         = Column(DOUBLE_PRECISION)
    updated_at        = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at        = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    host = relationship("Host")



class HostsModel(Base):
    __tablename__ = 'host'

    host_id           = Column(VARCHAR(50), primary_key=True)
    host_name         = Column(VARCHAR(50))
    number_of_reviews = Column(INTEGER)
    rating            = Column(REAL)
    years_hosting     = Column(INTEGER)
    is_super_host     = Column(BOOLEAN)
    is_verified       = Column(BOOLEAN)
    profile_image     = Column(VARCHAR(500))
    about             = Column(VARCHAR(64000))
    host_details      = Column(SUPER)
    updated_at        = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at        = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    


class ReviewsModel(Base):
    __tablename__ = 'reviews'

    property_id        = Column(VARCHAR(50), ForeignKey('property.property'), nullable=False)
    review_id          = Column(VARCHAR(100), primary_key=True)
    reviewer_name      = Column(VARCHAR(50))
    comments           = Column(VARCHAR(64000))
    profile_image_url  = Column(VARCHAR(1000))
    review_date        = Column(TIMESTAMP)
    reviewer_location  = Column(VARCHAR(100))
    rating             = Column(REAL)
    language           = Column(VARCHAR(length=5))
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    property = relationship("Property")

class RequestTracker(Base):

    __tablename__ = 'request_tracker'

    id                 = Column(INTEGER , primary_key=True , autoincrement=True)
    url                = Column(VARCHAR(5000), nullable=False)
    status_code        = Column(INTEGER)
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    