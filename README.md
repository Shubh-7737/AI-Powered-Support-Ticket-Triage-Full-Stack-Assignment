# AI-Powered Support Ticket Triage (v4)

Full-stack assignment implementation with:
- Backend REST API (FastAPI)
- Local AI-style analyzer (keyword + heuristic rules, no external AI APIs)
- SQLite persistence
- Frontend UI (React) for submit + results + recent tickets
- Unit tests for classification and priority logic
- Dockerized backend and frontend with `docker-compose`

## Tech Stack
- Backend: Python, FastAPI, SQLAlchemy, SQLite
- Frontend: React + Vite
- Infra: Docker, Docker Compose

## Project Structure
```txt
.
├─ backend/
│  ├─ app/
│  │  ├─ api/tickets.py
│  │  ├─ analyzer/engine.py
│  │  ├─ config/rules.json
│  │  ├─ database.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ services/ticket_service.py
│  │  └─ main.py
│  ├─ tests/test_analyzer.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ src/App.jsx
│  ├─ src/styles.css
│  ├─ Dockerfile
│  └─ nginx.conf
├─ docker-compose.yml
└─ README.md
```

## Functional Coverage
- `POST /tickets/analyze`
  - Accepts `{ "message": "..." }`
  - Validates input
  - Runs local analyzer logic
  - Persists ticket + analysis to SQLite
  - Returns category, priority, urgency, confidence, signals, keywords
- `GET /tickets?limit=20`
  - Returns latest analyzed tickets first

Supported categories:
- Billing
- Technical
- Account
- Feature Request
- Other

Priorities:
- P0 (critical)
- P1 (high)
- P2 (medium)
- P3 (low)

## Analyzer Design (Local NLP / Heuristic)
- Config-driven rules in `backend/app/config/rules.json`
- Keyword matching for category classification
- Urgency terms detection (`urgent`, `asap`, `down`, etc.)
- Severity phrase checks to set baseline priority
- Heuristic fallback priority based on urgency + category
- Confidence score from combined signal strength
- Keyword extraction from normalized text with stopword filtering

### Custom Rule (Required Twist)
Custom rule: `security_override`
- If message contains security indicators (`security`, `breach`, `hacked`, `unauthorized access`, `leak`)
- Force:
  - `category = Technical`
  - `priority = P0`

Rationale:
- Security incidents generally have high blast radius and compliance risk.
- Treating them as critical by default helps reduce response latency.

## Frontend Features
- Textarea ticket input
- Submit to backend analyze API
- Result panel: category, priority, urgency, confidence, signals, keywords
- Recent tickets table (latest first)
- Loading and error states

## Run Locally (Docker)
```bash
docker-compose up --build
```

Apps:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

## Run Without Docker

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## API Examples

Analyze ticket:
```bash
curl -X POST http://localhost:8000/tickets/analyze \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Production is down, urgent outage affecting payment checkout\"}"
```

List tickets:
```bash
curl "http://localhost:8000/tickets?limit=10"
```

## Tests
Run:
```bash
cd backend
pytest -q
```

Coverage includes:
- Billing classification
- Technical outage priority
- Account ticket handling
- Custom security override rule
- Other category fallback
- API integration tests for:
  - `POST /tickets/analyze`
  - `GET /tickets`
  - validation/error path for stripped short messages

## Design Notes
- Separation of concerns:
  - Controller: request/response handling
  - Service: orchestration + persistence
  - Analyzer: classification/prioritization logic
  - Config: rule sets isolated from code for easier tuning
- Data model stores message + all derived fields + timestamps for auditability.
- JSON-encoded `signals` and `keywords` keep schema simple while preserving structured output.

## Reflection (Required, <= 1 Page)
I chose FastAPI + SQLite because it provides a lightweight, dependable stack for local development and Dockerized demo delivery. The API surface is intentionally small (`POST /tickets/analyze`, `GET /tickets`) to keep the data flow explicit and easy to test end-to-end. The ticket table stores both raw input and derived analysis so we can inspect decision quality over time and reproduce outputs.

The analyzer is keyword and heuristic based, with rules externalized in JSON. This keeps logic transparent and easy to iterate: non-code updates to categories, urgency, and severity can be made by editing configuration. The trade-off is limited language understanding; phrasing variance and unseen synonyms can reduce accuracy versus a learned NLP model.

I added a custom `security_override` rule because security incidents deserve conservative prioritization. This improves operational safety but may over-prioritize some false positives where users use security-adjacent language casually. With more time, I would add:
- weighted scoring and phrase proximity
- rule evaluation traces for explainability in UI
- richer tests including API integration tests
- authentication, pagination, and better DB normalization for production-scale use
- optional active-learning feedback loop to tune rules from human corrections

## Demo Video Checklist (2-5 mins)
- Start app with `docker-compose up --build`
- Submit at least 3 tickets from UI
- Show result panel fields
- Show recent tickets list updating
- Demonstrate custom rule:
  - example input: `"Possible unauthorized access and data leak detected"`
  - expected output includes `priority: P0` and security override signal
