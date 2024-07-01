from sqlalchemy import Column, Integer, String, Text, Float, TIMESTAMP, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GolfCourse(Base):
    __tablename__ = 'golf_courses'

    course_id = Column(Integer, primary_key=True)
    course_name = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)
    description = Column(Text)
    number_of_holes = Column(Integer)
    par = Column(Integer)
    yardage = Column(Integer)
    slope_rating = Column(Float)
    course_rating = Column(Float)
    architect = Column(String)
    year_built = Column(Integer)
    images = Column(Text)
    tee_details = Column(JSON)
    policies = Column(String)
    rental_services = Column(String)
    practice_instructions = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
