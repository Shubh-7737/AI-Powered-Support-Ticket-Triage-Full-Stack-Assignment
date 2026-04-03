from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_analyze_ticket_api_returns_analysis_and_persists():
    payload = {"message": "Production is down and users cannot login. urgent outage"}
    response = client.post("/tickets/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] in {"Technical", "Account"}
    assert data["priority"] == "P0"
    assert data["urgency"] == "High"
    assert isinstance(data["keywords"], list)
    assert "id" in data


def test_analyze_ticket_api_custom_security_rule():
    payload = {"message": "Possible unauthorized access and data leak detected"}
    response = client.post("/tickets/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Technical"
    assert data["priority"] == "P0"
    assert "custom:security_override" in data["signals"]


def test_list_tickets_api_returns_records():
    client.post("/tickets/analyze", json={"message": "Need refund for double charge on invoice"})
    client.post("/tickets/analyze", json={"message": "Please add dark mode feature for dashboard"})

    response = client.get("/tickets?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert all("message" in item and "category" in item and "priority" in item for item in data)


def test_analyze_ticket_stripped_short_message_rejected():
    response = client.post("/tickets/analyze", json={"message": "     " * 2})
    assert response.status_code == 400
