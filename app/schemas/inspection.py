from pydantic import BaseModel
from datetime import date
from typing import Optional


class InspectionBase(BaseModel):
    inspector_name: str
    inspection_date: date
    target_type: str  # "ship", "store", "truck"
    ship_id: Optional[int] = None
    location_name: Optional[str] = None
    violation_found: bool = False
    violation_description: Optional[str] = None


class InspectionCreate(InspectionBase):
    pass


class InspectionResponse(InspectionBase):
    id: int

    class Config:
        from_attributes = True


class FineBase(BaseModel):
    inspection_id: int
    amount: float
    issued_date: date
    paid: bool = False


class FineCreate(FineBase):
    pass


class FineResponse(FineBase):
    id: int

    class Config:
        from_attributes = True