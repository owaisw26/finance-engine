# Day 3 Reflection

## What FastAPI Does In This Architecture

FastAPI is the platform's HTTP boundary. It receives requests from the frontend or external clients, validates input and output through typed models, and routes those requests to backend services.

In this project, FastAPI should stay focused on API orchestration. It should not become the place where ingestion logic, database logic, AI enrichment, and search algorithms are all mixed together.

## REST API Foundation

REST endpoints expose system capabilities as stable contracts. A route like `GET /health` is simple, but it proves several important things:

- The API process can start.
- The app can load configuration.
- The route layer is wired correctly.
- The response shape is typed and testable.
- The service can be checked by Docker, CI, or monitoring.

Later endpoints such as `POST /ingest/manual`, `GET /events`, and `POST /semantic-search` should follow the same pattern: clear route, typed schema, service layer behind it, and tests.

## Why Request And Response Models Matter

Pydantic schemas make API contracts explicit. Instead of returning arbitrary dictionaries everywhere, response models define what the frontend and other clients can rely on.

This matters because the frontend, workers, tests, and docs will all depend on stable shapes. If response shapes drift casually, the system becomes harder to extend and debug.

## Why Config Loading Matters

The backend must run in different environments without code changes:

- local terminal development
- Docker Compose
- CI
- future deployment

Configuration values like database URLs, Redis URLs, API keys, ports, and environment names belong in environment variables, not hardcoded into business logic.

Using a settings object gives the app one typed place to read configuration from.

## Why Structured Logging Matters

Plain text logs are useful while experimenting, but production-style systems need logs that can be filtered and searched.

Structured logs let the platform record fields such as:

- request method
- request path
- status code
- duration
- environment
- version
- later: job ID, source name, document ID, retry count, and pipeline stage

This becomes important when ingestion jobs, workers, AI providers, or search pipelines fail.

## Day 3 Decision

Use a small FastAPI app factory with separate modules for config, logging, schemas, and routes. This avoids turning `main.py` into a dumping ground and gives future database, ingestion, search, and worker code clean places to connect.
