from sqlalchemy import Column, Integer, String, Text, Float, func, ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_redshift.dialect import SUPER, VARCHAR, INTEGER, REAL, TIMESTAMP, DOUBLE_PRECISION, SMALLINT, BOOLEAN
from sqlalchemy.orm import relationship

Base = declarative_base()

class GolfCourse(Base):
    __tablename__ = 'golf_courses'

    course_id = Column(INTEGER, primary_key=True)
    course_name = Column(VARCHAR(255))
    address = Column(VARCHAR(255))
    city = Column(VARCHAR(100))
    state = Column(VARCHAR(100))
    country = Column(VARCHAR(100))
    postal_code = Column(VARCHAR(50))
    description = Column(VARCHAR(64000))
    number_of_holes = Column(SMALLINT)
    par = Column(SMALLINT)
    yardage = Column(INTEGER)
    slope_rating = Column(REAL)
    course_rating = Column(REAL)
    architect = Column(VARCHAR(1000))
    year_built = Column(SMALLINT)
    images = Column(VARCHAR(64000))
    tee_details = Column(SUPER)
    policies = Column(SUPER)
    rental_services = Column(SUPER)
    practice_instructions = Column(SUPER)
    latitude = Column(DOUBLE_PRECISION)
    longitude = Column(DOUBLE_PRECISION)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


    tee_times = relationship('TeeTime', back_populates='golf_course')


class TeeTime(Base):
    __tablename__ = 'tee_times'

    course_id = Column(Integer, ForeignKey('golf_courses.course_id'), nullable=False)
    tee_time_id = Column(Integer, nullable=False)
    tee_datetime = Column(TIMESTAMP)
    display_rate = Column(REAL, nullable=False)
    currency = Column(VARCHAR(10), nullable=False)
    display_fee_rate = Column(BOOLEAN, nullable=True)
    max_transaction_fee = Column(Float, nullable=True)
    hole_count = Column(Integer, nullable=True)
    rate_name = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('course_id', 'tee_time_id'),
    )