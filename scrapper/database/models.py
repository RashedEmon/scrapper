from sqlalchemy import Column, Integer, String, Text, Float, Enum, Date, Time, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class GolfCourse(Base):
    __tablename__ = 'GolfCourses'

    CourseID = Column(Integer, primary_key=True, autoincrement=True)
    CourseName = Column(String)
    Address = Column(String)
    City = Column(String)
    StateProvince = Column(String)
    Country = Column(String)
    PostalCode = Column(String)
    PhoneNumber = Column(String)
    WebsiteURL = Column(String)
    Description = Column(Text)
    NumberOfHoles = Column(Integer)
    Par = Column(Integer)
    Yardage = Column(Integer)
    SlopeRating = Column(Float)
    CourseRating = Column(Float)
    GreenFees = Column(String)
    BookingURL = Column(String)
    CourseType = Column(Enum('Public', 'Private', 'Resort', name='course_type_enum'))
    Architect = Column(String)
    YearBuilt = Column(Integer)
    Amenities = Column(String)
    Images = Column(Text)
    Latitude = Column(Float)
    Longitude = Column(Float)
    LastUpdated = Column(TIMESTAMP)

    reviews = relationship('Review', backref='golf_course', cascade='all, delete-orphan')
    tee_times = relationship('TeeTime', backref='golf_course', cascade='all, delete-orphan')
    facilities = relationship('Facility', backref='golf_course', cascade='all, delete-orphan')
    services = relationship('Service', backref='golf_course', cascade='all, delete-orphan')


class Review(Base):
    __tablename__ = 'Reviews'

    ReviewID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey('GolfCourses.CourseID'))
    ReviewerName = Column(String)
    ReviewText = Column(Text)
    Rating = Column(Integer)
    ReviewDate = Column(TIMESTAMP)


class TeeTime(Base):
    __tablename__ = 'TeeTimes'

    TeeTimeID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey('GolfCourses.CourseID'))
    Date = Column(Date)
    Time = Column(Time)
    Price = Column(DECIMAL)
    BookingURL = Column(String)


class Facility(Base):
    __tablename__ = 'Facilities'

    FacilityID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey('GolfCourses.CourseID'))
    FacilityType = Column(Enum('Driving Range', 'Putting Green', 'Clubhouse', 'Pro Shop', name='facility_type_enum'))
    Details = Column(String)


class Service(Base):
    __tablename__ = 'Services'

    ServiceID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey('GolfCourses.CourseID'))
    ServiceType = Column(Enum('Lessons', 'Rentals', 'Catering', name='service_type_enum'))
    Details = Column(String)
