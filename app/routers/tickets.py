from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models.ticket import Ticket, AmateurCatch
from app.schemas.ticket import (
    TicketCreate, TicketResponse,
    AmateurCatchCreate, AmateurCatchResponse,
)

router = APIRouter(prefix="/tickets", tags=["Amateur Tickets"])
templates = Jinja2Templates(directory="app/templates")

DURATION_DAYS = {"daily": 1, "weekly": 7, "annual": 365}

BASE_PRICE = {
    "daily": {"adult": 6.0, "minor": 4.0, "pensioner": 4.0},
    "weekly": {"adult": 18.0, "minor": 12.0, "pensioner": 12.0},
    "annual": {"adult": 35.0, "minor": 22.0, "pensioner": 22.0},
}


def calculate_price(duration: str, is_minor: bool, is_pensioner: bool, is_disabled: bool) -> float:
    if is_disabled:
        return 0.0
    rates = BASE_PRICE.get(duration, BASE_PRICE["daily"])
    if is_minor:
        return rates["minor"]
    if is_pensioner:
        return rates["pensioner"]
    return rates["adult"]


@router.post("/", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    if ticket.is_disabled and not ticket.telk_decision_number:
        raise HTTPException(
            status_code=400,
            detail="telk_decision_number is required for disabled (free) tickets"
        )
    if ticket.is_disabled and ticket.price != 0:
        raise HTTPException(
            status_code=400,
            detail="Disabled tickets must be free (price = 0)"
        )

    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()


@router.get("/page", include_in_schema=False)
def tickets_page(request: Request, db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    t = request.state.t
    return templates.TemplateResponse(request=request, name="tickets.html", context={"tickets": tickets, "t": t, "lang": request.state.lang})


@router.post("/new", include_in_schema=False)
def create_ticket_form(
    holder_name: str = Form(...),
    issue_date: date = Form(...),
    duration: str = Form(...),
    is_minor: bool = Form(False),
    is_pensioner: bool = Form(False),
    is_disabled: bool = Form(False),
    db: Session = Depends(get_db),
):
    days = DURATION_DAYS.get(duration, 1)
    expiry_date = issue_date + timedelta(days=days)
    price = calculate_price(duration, is_minor, is_pensioner, is_disabled)

    db_ticket = Ticket(
        holder_name=holder_name,
        issue_date=issue_date,
        expiry_date=expiry_date,
        price=price,
        is_minor=is_minor,
        is_pensioner=is_pensioner,
        is_disabled=is_disabled,
    )
    db.add(db_ticket)
    db.commit()
    return RedirectResponse(url="/tickets/page", status_code=303)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/{ticket_id}/validity")
def check_validity(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    is_valid = ticket.expiry_date >= date.today()
    return {"ticket_id": ticket_id, "valid": is_valid, "expiry_date": ticket.expiry_date}


@router.post("/{ticket_id}/catch", response_model=AmateurCatchResponse)
def log_catch(ticket_id: int, catch: AmateurCatchCreate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.expiry_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot log a catch on an expired ticket")

    catch_data = catch.model_dump()
    catch_data["ticket_id"] = ticket_id

    db_catch = AmateurCatch(**catch_data)
    db.add(db_catch)
    db.commit()
    db.refresh(db_catch)
    return db_catch


@router.get("/{ticket_id}/catches", response_model=list[AmateurCatchResponse])
def list_catches(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db.query(AmateurCatch).filter(AmateurCatch.ticket_id == ticket_id).all()