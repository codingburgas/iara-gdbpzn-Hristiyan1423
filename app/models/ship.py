from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)

    # Identification info
    international_number = Column(String, unique=True, index=True, nullable=False)
    callsign = Column(String, nullable=True)
    marking = Column(String, nullable=True)

    # Owner info
    owner_name = Column(String, nullable=False)
    owner_contact = Column(String, nullable=True)

    # Captain info
    captain_name = Column(String, nullable=True)

    # Technical parameters
    length = Column(Float, nullable=True)          # meters
    width = Column(Float, nullable=True)            # meters
    tonnage = Column(Float, nullable=True)           # tons
    draft = Column(Float, nullable=True)              # meters
    engine_power = Column(Float, nullable=True)       # kW or HP
    fuel_type = Column(String, nullable=True)

    # Relationships (set up once Permit model is filled in)
    permits = relationship("Permit", back_populates="ship")