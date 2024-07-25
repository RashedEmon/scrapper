from sqlalchemy import Column, func, ForeignKey, VARCHAR, INTEGER, REAL, TIMESTAMP, FLOAT, SMALLINT, BOOLEAN, TEXT, JSON
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from scrapper.database.connection import Base

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
    images = Column(TEXT)
    tee_details = Column(JSON)
    policies = Column(JSON)
    rental_services = Column(JSON)
    practice_instructions = Column(JSON)
    latitude = Column(FLOAT)
    longitude = Column(FLOAT)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)



class TeeTime(Base):
    __tablename__ = 'tee_times'

    course_id = Column(INTEGER, ForeignKey('golf_courses.course_id'), nullable=False)
    tee_time_id = Column(INTEGER, nullable=False)
    tee_datetime = Column(TIMESTAMP)
    display_rate = Column(REAL, nullable=False)
    currency = Column(VARCHAR(10), nullable=False)
    display_fee_rate = Column(BOOLEAN, nullable=True)
    max_transaction_fee = Column(REAL, nullable=True)
    hole_count = Column(INTEGER, nullable=True)
    rate_name = Column(VARCHAR(100), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('course_id', 'tee_time_id'),
    )

    golf_course = relationship('GolfCourse')