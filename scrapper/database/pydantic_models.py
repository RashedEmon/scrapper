from pydantic import BaseModel
from typing import Optional, Dict

class PydanticGolfCourse(BaseModel):
    course_id: int
    course_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    description: Optional[str] = None
    number_of_holes: Optional[int] = None
    par: Optional[int] = None
    yardage: Optional[int] = None
    slope_rating: Optional[float] = None
    course_rating: Optional[float] = None
    architect: Optional[str] = None
    year_built: Optional[int] = None
    images: Optional[str] = None
    tee_details: Optional[str] = None
    policies: Optional[str] = None
    rental_services: Optional[str] = None
    practice_instructions: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True


class PydanticTeeDetails(BaseModel):
    course_id: int
    tee_time_id: int
    tee_datetime: str
    display_rate: float
    currency: str
    display_fee_rate: Optional[bool] = None
    max_transaction_fee: Optional[float] = None
    hole_count: Optional[int] = None
    rate_name: Optional[str] = None

    class Config:
        from_attributes = True