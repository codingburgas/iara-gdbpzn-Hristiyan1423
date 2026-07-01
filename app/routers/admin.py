from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ship import Ship
from app.models.permit import Permit
from app.models.ticket import Ticket
from app.admin_auth import is_admin, ADMIN_PASSWORD, ADMIN_COOKIE_VALUE
from datetime import date
router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="admin_login.html",
        context={"t": request.state.t, "lang": request.state.lang}
    )


@router.post("/login", include_in_schema=False)
def login_submit(password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_session", value=ADMIN_COOKIE_VALUE, httponly=True, max_age=3600 * 8)
        return response
    return RedirectResponse(url="/admin/login?error=1", status_code=303)


@router.get("/logout", include_in_schema=False)
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response


@router.get("/dashboard", include_in_schema=False)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    ships = db.query(Ship).all()
    permits = db.query(Permit).all()
    tickets = db.query(Ticket).all()
    return templates.TemplateResponse(
        request=request, name="admin_dashboard.html",
        context={"ships": ships, "permits": permits, "tickets": tickets, "t": request.state.t, "lang": request.state.lang}
    )


@router.post("/ships/{ship_id}/delete", include_in_schema=False)
def admin_delete_ship(ship_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if ship:
        db.delete(ship)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/permits/{permit_id}/revoke", include_in_schema=False)
def admin_revoke_permit(permit_id: int, request: Request, reason: str = Form("Revoked by staff"), db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if permit:
        permit.is_revoked = True
        permit.revoked_reason = reason
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/permits/{permit_id}/delete", include_in_schema=False)
def admin_delete_permit(permit_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if permit:
        db.delete(permit)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/tickets/{ticket_id}/delete", include_in_schema=False)
def admin_delete_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)
@router.get("/ships/{ship_id}/edit", include_in_schema=False)
def admin_edit_ship_page(ship_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request, name="admin_edit_ship.html",
        context={"ship": ship, "t": request.state.t, "lang": request.state.lang}
    )


@router.post("/ships/{ship_id}/edit", include_in_schema=False)
def admin_edit_ship_submit(
    ship_id: int, request: Request,
    international_number: str = Form(...),
    owner_name: str = Form(...),
    captain_name: str = Form(None),
    callsign: str = Form(None),
    length: float = Form(None),
    tonnage: float = Form(None),
    db: Session = Depends(get_db),
):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if ship:
        ship.international_number = international_number
        ship.owner_name = owner_name
        ship.captain_name = captain_name
        ship.callsign = callsign
        ship.length = length
        ship.tonnage = tonnage
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/permits/{permit_id}/edit", include_in_schema=False)
def admin_edit_permit_page(permit_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request, name="admin_edit_permit.html",
        context={"permit": permit, "t": request.state.t, "lang": request.state.lang}
    )


@router.post("/permits/{permit_id}/edit", include_in_schema=False)
def admin_edit_permit_submit(
    permit_id: int, request: Request,
    holder_name: str = Form(...),
    captain_name: str = Form(None),
    expiry_date: date = Form(...),
    gear_description: str = Form(None),
    db: Session = Depends(get_db),
):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if permit:
        permit.holder_name = holder_name
        permit.captain_name = captain_name
        permit.expiry_date = expiry_date
        permit.gear_description = gear_description
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)