from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.ship import Ship
from app.schemas.ship import ShipCreate, ShipResponse

router = APIRouter(prefix="/ships", tags=["Ships"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/", response_model=ShipResponse)
def create_ship(ship: ShipCreate, db: Session = Depends(get_db)):
    db_ship = Ship(**ship.model_dump())
    db.add(db_ship)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A ship with this international number already exists.")
    db.refresh(db_ship)
    return db_ship


@router.get("/", response_model=list[ShipResponse])
def list_ships(db: Session = Depends(get_db)):
    return db.query(Ship).all()


@router.get("/page", include_in_schema=False)
def ships_page(request: Request, db: Session = Depends(get_db)):
    ships = db.query(Ship).all()
    t = request.state.t
    return templates.TemplateResponse(request=request, name="ships.html", context={"ships": ships, "t": t, "lang": request.state.lang})


@router.post("/new", include_in_schema=False)
def create_ship_form(
    international_number: str = Form(...),
    callsign: str = Form(None),
    owner_name: str = Form(...),
    captain_name: str = Form(None),
    length: float = Form(None),
    tonnage: float = Form(None),
    db: Session = Depends(get_db),
):
    db_ship = Ship(
        international_number=international_number,
        callsign=callsign,
        owner_name=owner_name,
        captain_name=captain_name,
        length=length,
        tonnage=tonnage,
    )
    db.add(db_ship)
    db.commit()
    return RedirectResponse(url="/ships/page", status_code=303)


@router.get("/{ship_id}", response_model=ShipResponse)
def get_ship(ship_id: int, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    return ship


@router.put("/{ship_id}", response_model=ShipResponse)
def update_ship(ship_id: int, updated: ShipCreate, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    for field, value in updated.model_dump().items():
        setattr(ship, field, value)
    db.commit()
    db.refresh(ship)
    return ship


@router.delete("/{ship_id}")
def delete_ship(ship_id: int, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    db.delete(ship)
    db.commit()
    return {"message": "Ship deleted successfully"}