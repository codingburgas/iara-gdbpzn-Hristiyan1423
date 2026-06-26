from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.ship import Ship
from app.schemas.ship import ShipCreate, ShipResponse

router = APIRouter(prefix="/ships", tags=["Ships"])


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