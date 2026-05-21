# Finance Engine

Finance Engine is an AI financial intelligence platform focused on market event analysis, narrative detection, semantic search, and research workflows.

The project is not a stock predictor, trading bot, budgeting app, or generic AI wrapper. It is a backend-heavy distributed AI data platform with finance as the domain layer.

## Day 1 Status

Day 1 establishes the product boundary and architecture before implementation begins.

- MVP definition: [docs/day-01-product-architecture.md](docs/day-01-product-architecture.md)
- Reflection notes: [docs/reflections/day-01.md](docs/reflections/day-01.md)

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
