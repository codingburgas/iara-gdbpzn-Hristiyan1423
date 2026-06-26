from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class FishingTrip(Base):
    __tablename__ = "fishing_trips"

    id = Column(Integer, primary_key=True, index=True)

    permit_id = Column(Integer, ForeignKey("permits.id"), nullable=False)

    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)

    # Relationships
    permit = relationship("Permit", back_populates="trips")
    log_entries = relationship("LogEntry", back_populates="trip")


class LogEntry(Base):
    """
    Electronic logbook entry — required for ships over 10m.
    Each entry records one fishing operation within a trip.
    """
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)

    trip_id = Column(Integer, ForeignKey("fishing_trips.id"), nullable=False)

    start_time = Column(String, nullable=False)   # could upgrade to DateTime later
    end_time = Column(String, nullable=True)
    location = Column(String, nullable=False)       # e.g. coordinates or zone name
    gear_used = Column(String, nullable=True)
    catch_amount_kg = Column(Float, nullable=True)
    species = Column(String, nullable=True)

    # Relationships
    trip = relationship("FishingTrip", back_populates="log_entries")