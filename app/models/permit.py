from app.models.logbook import FishingTrip
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Permit(Base):
    __tablename__ = "permits"

    id = Column(Integer, primary_key=True, index=True)

    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)

    # Validity
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    is_revoked = Column(Boolean, default=False)
    revoked_reason = Column(String, nullable=True)

    # Who is fishing
    holder_name = Column(String, nullable=False)   # owner or user of the ship
    captain_name = Column(String, nullable=True)

    # Gear used (kept simple as text for now; could become its own table later)
    gear_description = Column(String, nullable=True)

    # Relationships
    ship = relationship("Ship", back_populates="permits")
    trips = relationship("FishingTrip", back_populates="permit")