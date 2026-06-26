from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.permit import Permit
from app.models.ship import Ship
from app.schemas.permit import PermitCreate, PermitResponse

router = APIRouter(prefix="/permits", tags=["Permits"])


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