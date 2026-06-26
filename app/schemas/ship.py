from pydantic import BaseModel
from typing import Optional


class ShipBase(BaseModel):
    international_number: str
    callsign: Optional[str] = None
    marking: Optional[str] = None
    owner_name: str
    owner_contact: Optional[str] = None
    captain_name: Optional[str] = None
    length: Optional[float] = None
    width: Optional[float] = None
    tonnage: Optional[float] = None
    draft: Optional[float] = None
    engine_power: Optional[float] = None
    fuel_type: Optional[str] = None


class ShipCreate(ShipBase):
    pass


class ShipResponse(ShipBase):
    id: int

    class Config:
        from_attributes = True