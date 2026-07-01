from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.permit import Permit
from app.models.ship import Ship
from app.schemas.permit import PermitCreate, PermitResponse

router = APIRouter(prefix="/permits", tags=["Permits"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/", response_model=PermitResponse)
def create_permit(permit: PermitCreate, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == permit.ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")

    db_permit = Permit(**permit.model_dump())
    db.add(db_permit)
    db.commit()
    db.refresh(db_permit)
    return db_permit


@router.get("/", response_model=list[PermitResponse])
def list_permits(db: Session = Depends(get_db)):
    return db.query(Permit).all()


@router.get("/page", include_in_schema=False)
def permits_page(request: Request, db: Session = Depends(get_db)):
    permits = db.query(Permit).all()
    t = request.state.t
    return templates.TemplateResponse(request=request, name="permits.html", context={"permits": permits, "t": t, "lang": request.state.lang})


@router.post("/new", include_in_schema=False)
def create_permit_form(
    ship_id: int = Form(...),
    holder_name: str = Form(...),
    captain_name: str = Form(None),
    issue_date: date = Form(...),
    expiry_date: date = Form(...),
    gear_description: str = Form(None),
    db: Session = Depends(get_db),
):
    db_permit = Permit(
        ship_id=ship_id,
        holder_name=holder_name,
        captain_name=captain_name,
        issue_date=issue_date,
        expiry_date=expiry_date,
        gear_description=gear_description,
    )
    db.add(db_permit)
    db.commit()
    return RedirectResponse(url="/permits/page", status_code=303)


@router.get("/{permit_id}", response_model=PermitResponse)
def get_permit(permit_id: int, db: Session = Depends(get_db)):
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    return permit


@router.patch("/{permit_id}/revoke", response_model=PermitResponse)
def revoke_permit(permit_id: int, reason: str, db: Session = Depends(get_db)):
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    permit.is_revoked = True
    permit.revoked_reason = reason
    db.commit()
    db.refresh(permit)
    return permit