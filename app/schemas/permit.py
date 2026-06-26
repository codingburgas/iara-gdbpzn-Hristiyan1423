from pydantic import BaseModel
from datetime import date
from typing import Optional


class PermitBase(BaseModel):
    ship_id: int
    issue_date: date
    expiry_date: date
    holder_name: str
    captain_name: Optional[str] = None
    gear_description: Optional[str] = None
    is_revoked: bool = False
    revoked_reason: Optional[str] = None


class PermitCreate(PermitBase):
    pass


class PermitResponse(PermitBase):
    id: int

    class Config:
        from_attributes = True