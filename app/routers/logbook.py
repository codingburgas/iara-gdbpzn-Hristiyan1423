from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.logbook import FishingTrip, LogEntry
from app.models.permit import Permit
from app.schemas.logbook import (
    FishingTripCreate, FishingTripResponse,
    LogEntryCreate, LogEntryResponse,
)

router = APIRouter(prefix="/trips", tags=["Fishing Trips & Logbook"])


@router.post("/", response_model=FishingTripResponse)
def create_trip(trip: FishingTripCreate, db: Session = Depends(get_db)):
    permit = db.query(Permit).filter(Permit.id == trip.permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    if permit.is_revoked:
        raise HTTPException(status_code=400, detail="Cannot start a trip on a revoked permit")

    db_trip = FishingTrip(**trip.model_dump())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@router.get("/", response_model=list[FishingTripResponse])
def list_trips(db: Session = Depends(get_db)):
    return db.query(FishingTrip).all()


@router.get("/{trip_id}", response_model=FishingTripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(FishingTrip).filter(FishingTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.post("/{trip_id}/log", response_model=LogEntryResponse)
def add_log_entry(trip_id: int, entry: LogEntryCreate, db: Session = Depends(get_db)):
    trip = db.query(FishingTrip).filter(FishingTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    entry_data = entry.model_dump()
    entry_data["trip_id"] = trip_id  # ensure it matches the path, ignore mismatched body value

    db_entry = LogEntry(**entry_data)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("/{trip_id}/log", response_model=list[LogEntryResponse])
def list_log_entries(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(FishingTrip).filter(FishingTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db.query(LogEntry).filter(LogEntry.trip_id == trip_id).all()