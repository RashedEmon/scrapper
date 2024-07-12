import dateutil.parser
from pydantic import BaseModel, Field, Json, field_validator
from typing import Optional, Dict, List, Any
from datetime import datetime
import dateutil


class Property(BaseModel):
    property_id: str = Field(..., max_length=50)
    property_name: Optional[str] = Field(None, max_length=256)
    country: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    amenities: Optional[List[Dict[str, Any]]]
    room_arrangement: Optional[List[Dict[str, Any]]] = None
    rating: Optional[float] = None
    detailed_review: Optional[List[Any]] = None
    number_of_reviews: Optional[int] = None
    images: Optional[List[str]] = None
    price: Optional[float] = None
    currency_code: Optional[str] = Field(None, max_length=5)
    facilities: Optional[List[str]] = None
    policies: Optional[List[Any]] = None
    host_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Host(BaseModel):
    host_id: str
    host_name: Optional[str] = Field(None, max_length=50)
    number_of_reviews: Optional[int] = None
    rating: Optional[float] = None
    years_hosting: Optional[int] = None
    is_super_host: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_image: Optional[str] = Field(None, max_length=200)
    about: Optional[str] = Field(None, max_length=64000)
    host_details: Optional[dict] = Field(None, max_length=50)

class Review(BaseModel):
    property_id: str
    review_id: str = Field(..., max_length=100)
    reviewer_name: Optional[str] = Field(None, max_length=50)
    comments: Optional[str] = Field(None, max_length=64000)
    profile_image_url: Optional[str] = Field(None, max_length=1000)
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
