from pydantic import BaseModel
from datetime import date
from typing import Optional


class TicketBase(BaseModel):
    holder_name: str
    holder_egn: Optional[str] = None
    issue_date: date
    expiry_date: date
    price: float
    is_minor: bool = False
    is_pensioner: bool = False
    is_disabled: bool = False
    telk_decision_number: Optional[str] = None


class TicketCreate(TicketBase):
    pass


class TicketResponse(TicketBase):
    id: int

    class Config:
        from_attributes = True


class AmateurCatchBase(BaseModel):
    ticket_id: int
    catch_date: date
    species: Optional[str] = None
    amount_kg: Optional[float] = None
    location: Optional[str] = None


class AmateurCatchCreate(AmateurCatchBase):
    pass


class AmateurCatchResponse(AmateurCatchBase):
    id: int

    class Config:
        from_attributes = True