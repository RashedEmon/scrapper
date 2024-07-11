from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Property(BaseModel):
    property_id: str = Field(..., max_length=50)
    property_name: Optional[str] = Field(None, max_length=256)
    country: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    amenities: Optional[str] = Field(None, max_length=50)
    room_arrangement: Optional[str] = None
    rating: Optional[float] = None
    detailed_review: Optional[dict] = None
    number_of_reviews: Optional[int] = None
    images: Optional[str] = Field(None, max_length=64000)
    price: Optional[float] = None
    currency_code: Optional[str] = Field(None, max_length=5)
    facilities: Optional[dict] = None
    policies: Optional[dict] = None
    host_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Host(BaseModel):
    host_id: int
    host_name: Optional[str] = Field(None, max_length=50)
    number_of_reviews: Optional[int] = None
    rating: Optional[float] = None
    years_hosting: Optional[int] = None
    is_super_host: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_image: Optional[str] = Field(None, max_length=200)
    about: Optional[str] = Field(None, max_length=64000)
    host_details: Optional[dict] = Field(None, max_length=50)

class Reviews(BaseModel):
    property_id: int
    review_id: str = Field(..., max_length=100)
    reviewer_name: Optional[str] = Field(None, max_length=50)
    comments: Optional[str] = Field(None, max_length=64000)
    profile_image_url: Optional[str] = Field(None, max_length=100)
    review_date: Optional[datetime] = None
    reviewer_location: Optional[str] = None
    rating: Optional[float] = None