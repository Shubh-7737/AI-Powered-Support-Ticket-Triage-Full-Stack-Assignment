from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.tickets import router as tickets_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Support Ticket Triage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets_router)


@app.get("/health")
def health():
    return {"status": "ok"}
