from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    holder_name = Column(String, nullable=False)
    holder_egn = Column(String, nullable=True)   # personal ID number, optional depending on privacy rules

    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)

    # Pricing tier — depends on age / pensioner / disability status
    price = Column(Float, nullable=False)
    is_minor = Column(Boolean, default=False)        # under 14
    is_pensioner = Column(Boolean, default=False)
    is_disabled = Column(Boolean, default=False)      # free ticket if true
    telk_decision_number = Column(String, nullable=True)  # required if is_disabled

    # Relationships
    catches = relationship("AmateurCatch", back_populates="ticket")


class AmateurCatch(Base):
    """
    A logged catch by an amateur fisherman, recorded via the mobile app.
    """
    __tablename__ = "amateur_catches"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)

    catch_date = Column(Date, nullable=False)
    species = Column(String, nullable=True)
    amount_kg = Column(Float, nullable=True)
    location = Column(String, nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="catches")
