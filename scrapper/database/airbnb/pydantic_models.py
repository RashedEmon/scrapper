import dateutil.parser
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import dateutil


class Property(BaseModel):
    property_id: str
    property_name: Optional[str] = None
    country: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    amenities: Optional[str] = None
    room_arrangement: Optional[str] = None
    rating: Optional[float] = None
    detailed_review: Optional[str] = None
    number_of_reviews: Optional[int] = None
    images: Optional[str] = None
    price: Optional[float] = None
    currency_code: Optional[str] = None
    facilities: Optional[str] = None
    policies: Optional[str] = None
    host_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Host(BaseModel):
    host_id: str
    host_name: str
    number_of_reviews: Optional[int] = None
    rating: Optional[float] = None
    years_hosting: Optional[int] = None
    is_super_host: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_image: Optional[str] = None
    about: Optional[str] = None
    host_details: Optional[str] = None

class Review(BaseModel):
    property_id: str
    review_id: str
    reviewer_name: Optional[str] = None
    comments: Optional[str] = None
    profile_image_url: Optional[str] = None
    review_date: Optional[datetime] = None
    reviewer_location: Optional[str] = None
    rating: Optional[float] = None
    language: Optional[str] = None

    @field_validator('review_date')
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            return dateutil.parser.isoparse(value)
        return value
