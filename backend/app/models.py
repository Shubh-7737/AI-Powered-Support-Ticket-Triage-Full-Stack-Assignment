from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    priority = Column(String(2), nullable=False)
    urgency = Column(String(16), nullable=False)
    confidence = Column(Float, nullable=False)
    signals = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
