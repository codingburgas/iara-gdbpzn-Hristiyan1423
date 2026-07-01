from pydantic import BaseModel
from datetime import date
from typing import Optional


class FishingTripBase(BaseModel):
    permit_id: int
    departure_date: date
    return_date: Optional[date] = None


class FishingTripCreate(FishingTripBase):
    pass


class FishingTripResponse(FishingTripBase):
    id: int

    class Config:
        from_attributes = True


class LogEntryBase(BaseModel):
    trip_id: int
    start_time: str
    end_time: Optional[str] = None
    location: str
    gear_used: Optional[str] = None
    catch_amount_kg: Optional[float] = None
    species: Optional[str] = None


class LogEntryCreate(LogEntryBase):
    pass


class LogEntryResponse(LogEntryBase):
    id: int

    class Config:
        from_attributes = True