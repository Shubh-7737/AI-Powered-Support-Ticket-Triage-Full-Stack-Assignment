import json
from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.analyzer.engine import analyze_ticket
from app.models import Ticket


def analyze_and_store_ticket(db: Session, message: str) -> Ticket:
    analysis = analyze_ticket(message)
    ticket = Ticket(
        message=message,
        category=analysis["category"],
        priority=analysis["priority"],
        urgency=analysis["urgency"],
        confidence=analysis["confidence"],
        signals=json.dumps(analysis["signals"]),
        keywords=json.dumps(analysis["keywords"]),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, limit: int = 50) -> List[Ticket]:
    return db.query(Ticket).order_by(desc(Ticket.created_at)).limit(limit).all()
