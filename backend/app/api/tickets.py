import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AnalyzeRequest, TicketResponse
from app.services.ticket_service import analyze_and_store_ticket, list_tickets

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _serialize_ticket(ticket) -> TicketResponse:
    return TicketResponse(
        id=ticket.id,
        message=ticket.message,
        category=ticket.category,
        priority=ticket.priority,
        urgency=ticket.urgency,
        confidence=ticket.confidence,
        signals=json.loads(ticket.signals),
        keywords=json.loads(ticket.keywords),
        created_at=ticket.created_at,
    )


@router.post("/analyze", response_model=TicketResponse)
def analyze_ticket_endpoint(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    message = payload.message.strip()
    if len(message) < 5:
        raise HTTPException(status_code=400, detail="Ticket message is too short.")
    ticket = analyze_and_store_ticket(db, message)
    return _serialize_ticket(ticket)


@router.get("", response_model=List[TicketResponse])
def list_tickets_endpoint(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    tickets = list_tickets(db, limit=limit)
    return [_serialize_ticket(ticket) for ticket in tickets]
