from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_redshift.dialect import SUPER, VARCHAR, INTEGER, REAL, TIMESTAMP, DOUBLE_PRECISION, SMALLINT, BOOLEAN
from sqlalchemy.orm import relationship

Base = declarative_base()

class Property(Base):
    __tablename__ = 'property'

    property_id       = Column(VARCHAR(50), primary_key=True)
    property_name     = Column(VARCHAR(256))
    country           = Column(VARCHAR(50))
    state             = Column(VARCHAR(50))
    city              = Column(VARCHAR(50))
    amenities         = Column(VARCHAR(50))
    rating            = Column(REAL)
    detailed_review   = Column(SUPER)
    number_of_reviews = Column(INTEGER)
    image_url         = Column(VARCHAR(64000))
    price             = Column(REAL)
    currency_code     = Column(VARCHAR(5))
    facilities        = Column(SUPER)
    things_to_know    = Column(SUPER)
    host_id           = Column(INTEGER, ForeignKey('host.host_id'))
    updated_at        = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at        = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    host = relationship("Host")



class Host(Base):
    __tablename__ = 'host'

    host_id           = Column(INTEGER, primary_key=True)
    host_name         = Column(VARCHAR(50))
    number_of_reviews = Column(INTEGER)
    rating            = Column(REAL)
    years_hosting     = Column(INTEGER)
    host_type         = Column(VARCHAR(50))
    address           = Column(VARCHAR(200))
    description       = Column(VARCHAR(64000))
    response_rate     = Column(VARCHAR(50))
    response_time     = Column(VARCHAR(50))
    profile_image     = Column(VARCHAR(200))
    updated_at        = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at        = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    


class Reviews(Base):
    __tablename__ = 'reviews'

    property_id        = Column(INTEGER, ForeignKey('property.property'), nullable=False)
    review_id          = Column(VARCHAR(100), primary_key=True)
    reviewer_name      = Column(VARCHAR(50))
    review_text        = Column(VARCHAR(64000))
    reviewer_image_url = Column(VARCHAR(100))
    review_date_time   = Column(TIMESTAMP)
    rating             = Column(REAL)
    updated_at         = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at         = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    property = relationship("Property")
    