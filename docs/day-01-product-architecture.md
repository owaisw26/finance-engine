# Day 1: Product And Architecture Grounding

## Purpose

Finance Engine is an intelligent market monitoring and financial research system. It ingests public financial information, converts raw material into structured intelligence, and exposes that intelligence through APIs, semantic search, narrative detection, conversational querying, and dashboards.

The core technical identity is:

> A distributed AI data platform with finance as the domain layer.

The finance domain gives the system realistic data, useful workflows, and portfolio relevance. The main engineering challenge is the backend/data/AI architecture: ingestion, async processing, enrichment, storage, retrieval, narrative detection, and explainable APIs.

## Concrete MVP Definition

The first complete MVP must let a user do this locally:

1. Start the platform with documented commands.
2. Ingest curated financial documents and at least one external news-style source.
3. Store raw documents with source metadata.
4. Convert raw documents into financial events.
5. Process events through an asynchronous enrichment pipeline.
6. Generate summaries, topic labels, sentiment labels, entities, and embeddings.
7. Search events by keyword and semantic meaning.
8. Group related events into narrative clusters.
9. Ask a research-style question and receive a grounded answer with cited events.
10. Inspect the system through a frontend dashboard.

This MVP is successful only if it works end to end. A beautiful frontend without working ingestion/search/enrichment is not enough. A backend with no visual research interface is also incomplete for portfolio presentation.

## What The System Does

- Monitors and ingests financial information from public sources and curated data.
- Preserves raw source documents for traceability and debugging.
- Normalizes information into structured financial events.
- Uses workers and queues to process enrichment outside the request path.
- Applies AI-style enrichment to summarize, classify, extract entities, embed, and cluster events.
- Detects emerging market narratives from related events.
- Supports semantic search over historical market developments.
- Supports conversational querying grounded in retrieved platform data.
- Provides a dashboard for event feeds, narratives, sentiment, search, and system status.

## What The System Does Not Do

- It does not predict stock prices.
- It does not recommend trades.
- It does not execute trades.
- It does not optimize portfolios.
- It does not model derivatives.
- It does not do high-frequency trading.
- It does not perform deep quantitative finance.
- It does not act as a budgeting or personal finance app.
- It does not present generic chatbot answers without retrieval from stored intelligence.

These non-goals matter because the project is meant to demonstrate backend engineering, distributed systems, data engineering, AI systems engineering, and production-style architecture.

## High-Level Architecture

```text
External Financial Sources
        |
        v
Ingestion Services
        |
        v
Message Queue
        |
        v
AI Processing Workers
        |
        v
PostgreSQL + Vector Storage
        |
        v
API Layer
        |
        v
Frontend Dashboard + AI Query Interface
```

## Subsystem Responsibilities

### External Financial Sources

Sources provide the raw material for the system: financial news, filings, earnings-style updates, macroeconomic releases, market commentary, and curated seed documents.

The MVP should begin with deterministic seed data and one reliable news-style connector so development does not depend entirely on external APIs.

### Ingestion Services

Ingestion services convert outside information into `RawDocument` records. They are responsible for source metadata, timestamps, content hashes, deduplication, and basic source reliability.

Ingestion should not perform expensive AI work directly. It should capture the source cleanly, then hand processing to the pipeline.

### Message Queue

The queue decouples ingestion from enrichment. HTTP requests should not wait for summarization, embedding generation, clustering, or retrieval preparation.

This gives the project an event-driven architecture and creates room to learn producers, consumers, retries, failure handling, and workload buffering.

### AI Processing Workers

Workers run enrichment jobs in the background. Their responsibilities include summarization, classification, sentiment detection, entity extraction, embedding generation, narrative clustering, and job status updates.

The first version should use deterministic fallbacks so the pipeline works without paid AI keys. Later versions can plug in real LLM and embedding providers.

### PostgreSQL + Vector Storage

PostgreSQL stores the durable intelligence layer: raw documents, events, entities, narratives, job runs, and source metadata.

Vector storage supports semantic retrieval. The plan uses pgvector so relational data and embeddings live in one operational database during the MVP.

### API Layer

The API exposes the platform capabilities to the frontend and future clients. It should provide clear contracts for ingestion, event retrieval, narrative lookup, keyword search, semantic search, conversational querying, and health checks.

### Frontend Dashboard + AI Query Interface

The frontend is not the core technical challenge, but it is essential for portfolio demonstration. It should make the backend system visible through event feeds, narrative tracking, sentiment visualization, search, and conversational research.

## Initial API Surface

- `GET /health`
- `POST /ingest/manual`
- `POST /ingest/run`
- `GET /events`
- `GET /events/{id}`
- `GET /entities`
- `GET /narratives`
- `GET /narratives/{id}`
- `GET /search?q=...`
- `POST /semantic-search`
- `POST /ask`

## Initial Data Model

- `RawDocument`: original source item, content, URL, source name, published timestamp, hash, ingestion metadata.
- `FinancialEvent`: structured market event derived from raw documents.
- `Entity`: company, ticker, sector, person, macro term, or theme.
- `NarrativeCluster`: group of related events with label, summary, strength, sentiment, and trend direction.
- `Embedding`: vector representation linked to an event or document.
- `JobRun`: pipeline execution record with status, timing, errors, retries, and job type.

## Day 1 Acceptance Criteria

- The MVP is defined in concrete user/system terms.
- The system's goals and non-goals are explicit.
- The high-level architecture is documented.
- The system is framed as learning + implementation, not just code generation.
- The next implementation step is clear: repo/tooling setup for backend, frontend, infrastructure, scripts, and docs.
