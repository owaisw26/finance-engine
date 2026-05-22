# Infrastructure

Infrastructure starts local-first with Docker Compose.

Current services:

- `postgres`: PostgreSQL with pgvector support.
- `redis`: queue and cache infrastructure.
- `backend`: FastAPI service.
- `worker`: background processing placeholder.
- `frontend`: Vite React dashboard.

The architecture is intentionally simple for the first working path. Service boundaries exist now so queues, workers, storage, and observability can be expanded without reshaping the repo later.
