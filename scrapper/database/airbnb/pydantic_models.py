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
    rating: Optional[float] = None
    detailed_review: Optional[dict] = None
    number_of_reviews: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=64000)
    price: Optional[float] = None
    currency_code: Optional[str] = Field(None, max_length=5)
    facilities: Optional[dict] = None
    things_to_know: Optional[dict] = None
    host_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Host(BaseModel):
    host_id: int
    host_name: Optional[str] = Field(None, max_length=50)
    number_of_reviews: Optional[int] = None
    rating: Optional[float] = None
    years_hosting: Optional[int] = None
    host_type: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=64000)
    response_rate: Optional[str] = Field(None, max_length=50)
    response_time: Optional[str] = Field(None, max_length=50)
    profile_image: Optional[str] = Field(None, max_length=200)

class Reviews(BaseModel):
    property_id: int
    review_id: str = Field(..., max_length=100)
    reviewer_name: Optional[str] = Field(None, max_length=50)
    review_text: Optional[str] = Field(None, max_length=64000)
    reviewer_image_url: Optional[str] = Field(None, max_length=100)
    review_date_time: Optional[datetime] = None
    rating: Optional[float] = None