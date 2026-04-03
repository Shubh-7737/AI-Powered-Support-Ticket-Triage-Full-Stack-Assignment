from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=5, max_length=5000)


class AnalysisResult(BaseModel):
    category: str
    priority: str
    urgency: str
    confidence: float
    signals: List[str]
    keywords: List[str]


class TicketResponse(AnalysisResult):
    id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
