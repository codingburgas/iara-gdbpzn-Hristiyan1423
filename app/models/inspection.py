from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)

    inspector_name = Column(String, nullable=False)
    inspection_date = Column(Date, nullable=False)

    # What was inspected — only one of these should be filled in per inspection
    target_type = Column(String, nullable=False)  # "ship", "store", "truck"
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=True)
    location_name = Column(String, nullable=True)  # store/truck identifier or address

    # Outcome
    violation_found = Column(Boolean, default=False)
    violation_description = Column(String, nullable=True)

    # Relationships
    ship = relationship("Ship")
    fine = relationship("Fine", back_populates="inspection", uselist=False)


class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)

    inspection_id = Column(Integer, ForeignKey("inspections.id"), unique=True, nullable=False)

    amount = Column(Float, nullable=False)
    issued_date = Column(Date, nullable=False)
    paid = Column(Boolean, default=False)

    # Relationships
    inspection = relationship("Inspection", back_populates="fine")