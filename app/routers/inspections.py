from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import Inspection, Fine
from app.models.ship import Ship
from app.schemas.inspection import (
    InspectionCreate, InspectionResponse,
    FineCreate, FineResponse,
)

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post("/", response_model=InspectionResponse)
def create_inspection(inspection: InspectionCreate, db: Session = Depends(get_db)):
    if inspection.target_type not in ("ship", "store", "truck"):
        raise HTTPException(status_code=400, detail="target_type must be 'ship', 'store', or 'truck'")

    if inspection.target_type == "ship":
        if not inspection.ship_id:
            raise HTTPException(status_code=400, detail="ship_id is required when target_type is 'ship'")
        ship = db.query(Ship).filter(Ship.id == inspection.ship_id).first()
        if not ship:
            raise HTTPException(status_code=404, detail="Ship not found")

    db_inspection = Inspection(**inspection.model_dump())
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


@router.get("/", response_model=list[InspectionResponse])
def list_inspections(db: Session = Depends(get_db)):
    return db.query(Inspection).all()


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.post("/{inspection_id}/fine", response_model=FineResponse)
def issue_fine(inspection_id: int, fine: FineCreate, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if not inspection.violation_found:
        raise HTTPException(status_code=400, detail="Cannot issue a fine for an inspection with no violation found")

    existing_fine = db.query(Fine).filter(Fine.inspection_id == inspection_id).first()
    if existing_fine:
        raise HTTPException(status_code=400, detail="A fine has already been issued for this inspection")

    db_fine = Fine(**fine.model_dump())
    db.add(db_fine)
    db.commit()
    db.refresh(db_fine)
    return db_fine


@router.get("/{inspection_id}/fine", response_model=FineResponse)
def get_fine(inspection_id: int, db: Session = Depends(get_db)):
    fine = db.query(Fine).filter(Fine.inspection_id == inspection_id).first()
    if not fine:
        raise HTTPException(status_code=404, detail="No fine found for this inspection")
    return fine