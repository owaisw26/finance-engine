# Finance Engine

Finance Engine is an AI financial intelligence platform focused on market event analysis, narrative detection, semantic search, and research workflows.

The project is not a stock predictor, trading bot, budgeting app, or generic AI wrapper. It is a backend-heavy distributed AI data platform with finance as the domain layer.

## Day 1 Status

Day 1 established the product boundary and architecture before implementation begins.

- MVP definition: [docs/day-01-product-architecture.md](docs/day-01-product-architecture.md)
- Reflection notes: [docs/reflections/day-01.md](docs/reflections/day-01.md)

## Day 2 Status

Day 2 established the repo and local tooling structure.

- Backend service skeleton: [backend](backend)
- Frontend service skeleton: [frontend](frontend)
- Infrastructure notes: [infra/README.md](infra/README.md)
- Script placeholders: [scripts/README.md](scripts/README.md)
- Reflection notes: [docs/reflections/day-02.md](docs/reflections/day-02.md)

## Day 3 Status

Day 3 established the backend foundation.

- FastAPI app factory: [backend/app/main.py](backend/app/main.py)
- Environment config: [backend/app/core/config.py](backend/app/core/config.py)
- Structured logging: [backend/app/core/logging.py](backend/app/core/logging.py)
- Health route: [backend/app/api/routes/health.py](backend/app/api/routes/health.py)
- Reflection notes: [docs/reflections/day-03.md](docs/reflections/day-03.md)

## Day 4 Status

Day 4 established the initial database design.

- SQLAlchemy base/session: [backend/app/db](backend/app/db)
- Domain models: [backend/app/models](backend/app/models)
- Alembic migration setup: [backend/migrations](backend/migrations)
- Initial schema migration: [backend/migrations/versions/0001_initial_intelligence_schema.py](backend/migrations/versions/0001_initial_intelligence_schema.py)
- Reflection notes: [docs/reflections/day-04.md](docs/reflections/day-04.md)

## Day 5 Status

Day 5 established manual ingestion.

- Manual ingestion route: [backend/app/api/routes/ingestion.py](backend/app/api/routes/ingestion.py)
- Ingestion service: [backend/app/services/ingestion.py](backend/app/services/ingestion.py)
- Ingestion schemas: [backend/app/schemas/ingestion.py](backend/app/schemas/ingestion.py)
- Seed documents: [backend/seeds/manual_documents.json](backend/seeds/manual_documents.json)
- Reflection notes: [docs/reflections/day-05.md](docs/reflections/day-05.md)

## Target System Flow

```text
External Financial Sources
        |
Ingestion Services
        |
Message Queue
        |
AI Processing Workers
        |
PostgreSQL + Vector Storage
        |
API Layer
        |
Frontend Dashboard + AI Query Interface
```

## Core Capabilities

- Ingest financial news, filings, earnings-style updates, macro events, and curated seed data.
- Normalize raw documents into structured financial events.
- Enrich events with summaries, topics, sentiment, entities, embeddings, and narrative clusters.
- Search financial events through keyword and semantic retrieval.
- Answer research-style questions using retrieved platform data.
- Visualize event feeds, narratives, sentiment, search results, and system status.

## Learning + Implementation Approach

Every subsystem is built through the same loop:

```text
Learn the theory
        |
Build a small working version
        |
Reflect on tradeoffs
        |
Expand the system
```

The goal is to build a working product while developing interview-ready understanding of backend systems, distributed processing, AI workflows, search, data engineering, and production-style infrastructure.

## Local Setup

Prerequisites:

- Docker Desktop or compatible Docker runtime
- Python 3.12 for direct backend development
- Node.js 20 or newer for direct frontend development

Create local environment config:

```bash
cp .env.example .env
```

Run the full local stack:

```bash
docker compose up --build
```

Expected local services:

- Backend API: `http://localhost:8000`
- Backend health check: `http://localhost:8000/health`
- Frontend dashboard: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

Manual ingestion endpoint:

```bash
curl -X POST http://localhost:8000/ingest/manual \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "manual",
    "title": "NVIDIA reports stronger data center demand",
    "body": "NVIDIA reported stronger-than-expected data center revenue as cloud providers continued spending on AI infrastructure."
  }'
```

Run backend tests directly:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m pytest
```

Run database migrations:

```bash
alembic upgrade head
```

Run frontend directly:

```bash
cd frontend
npm install
npm run dev
```

## Repository Structure

```text
backend/      FastAPI API, domain services, worker code, tests
frontend/     React dashboard and research interface
infra/        Local infrastructure notes and future deployment material
scripts/      Repeatable developer/demo commands
docs/         Architecture notes and learning reflections
```

## Initial Data Model

```text
RawDocument
    |
    v
FinancialEvent <-> Entity
    |
    +-> Embedding
    |
    +-> NarrativeCluster

JobRun tracks pipeline execution and failures.
```
