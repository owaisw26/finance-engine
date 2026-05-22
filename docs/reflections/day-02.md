# Day 2 Reflection

## Why Separate Backend, Frontend, Worker, Infrastructure, And Docs

The project is a distributed AI data platform, so the repo should make system boundaries visible from the beginning.

- `backend` owns APIs, domain services, data models, and orchestration.
- `worker` behavior lives with backend code at first because workers share domain logic and models.
- `frontend` owns dashboard and research workflow presentation.
- `infra` owns local service topology and future deployment notes.
- `docs` records architectural decisions and learning artifacts.
- `scripts` will hold repeatable commands for seeding, demos, and smoke tests.

This avoids treating the project like a single-page app with a small API attached. The repo shape reinforces that ingestion, processing, storage, retrieval, and visualization are separate concerns.

## Why Local Reproducibility Matters

A portfolio project has to run reliably for the builder, reviewers, and interview demos. Docker Compose gives the system a predictable local environment with Postgres, Redis, API, worker, and frontend services.

Local reproducibility matters because:

- It reduces setup friction.
- It makes demos less fragile.
- It exposes infrastructure dependencies honestly.
- It prepares the project for CI and deployment later.
- It proves the architecture is more than isolated code snippets.

## Day 2 Decision

Use a local-first Docker Compose topology with service boundaries for backend, worker, frontend, Postgres, and Redis. Keep the first version lightweight, but make the structure production-shaped enough to support queues, vector storage, async workers, and dashboard development as the system grows.
