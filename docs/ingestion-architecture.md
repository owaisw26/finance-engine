# Ingestion Architecture

## Purpose

Ingestion is the boundary where external financial information becomes internal platform data.

Its job is to make incoming documents safe, traceable, and consistent. It should not do deep interpretation. Topic classification, sentiment, importance, entities, embeddings, and narrative clustering belong to enrichment workers.

## Current Ingestion Sources

Finance Engine currently supports two ingestion paths:

- Manual ingestion through `POST /ingest/manual`.
- RSS ingestion through `POST /ingest/run`.

Both paths converge on the same internal storage flow:

```text
incoming source item
        |
        v
IngestionDocument
        |
        v
content hash dedupe
        |
        v
RawDocument
        |
        v
FinancialEvent shell
        |
        v
JobRun
```

This shared path matters because future sources should not create their own database logic. A future SEC connector, news API connector, Reddit connector, or JSON seed importer should convert source-specific data into an `IngestionDocument` and then reuse the same ingestion service.

## Manual Ingestion Flow

Manual ingestion accepts source text directly from a caller.

```text
POST /ingest/manual
        |
        v
ManualIngestionRequest
        |
        v
IngestionDocument
        |
        v
_ingest_document()
```

It stores:

- source name
- optional source URL
- title
- body
- optional published timestamp
- optional metadata

The response returns IDs for the created or existing raw document and financial event.

## RSS Ingestion Flow

RSS ingestion fetches and parses an external feed.

```text
POST /ingest/run
        |
        v
fetch_rss_xml()
        |
        v
parse_rss_xml()
        |
        v
RssItem[]
        |
        v
IngestionDocument[]
        |
        v
_ingest_document()
```

The RSS connector handles source-specific work:

- HTTP request with a user agent.
- request timeout.
- XML parsing.
- title extraction.
- description/body extraction.
- link extraction.
- publication date parsing.
- HTML cleanup in descriptions.

After that, RSS items use the same database ingestion path as manual input.

## Deduplication

Deduplication is based on a SHA-256 content hash generated from normalized title and body.

```text
normalize(title + body)
        |
        v
SHA-256 hash
        |
        v
raw_documents.content_hash
```

If a matching hash already exists, the ingestion service returns `duplicate` and does not create another raw document, financial event, or job run.

This protects:

- event feeds from repeated documents
- narrative counts from duplicate evidence
- search results from duplicate hits
- workers from unnecessary enrichment

## Current Database Writes

For a new document, ingestion creates:

- `RawDocument`: source truth and traceability.
- `FinancialEvent`: first structured event shell.
- `JobRun`: record of ingestion work.

The initial `FinancialEvent` deliberately leaves these fields unenriched:

- `topic = None`
- `sentiment = None`
- `importance = 0`

Those will be filled by worker-driven enrichment later.

## Reliability Decisions

Current reliability choices:

- Source metadata is preserved.
- Duplicate documents are detected by content hash.
- RSS fetches use a timeout.
- RSS fetches send a user agent.
- RSS parsing tolerates missing URL and missing publication date.
- RSS parsing skips items missing title or description.
- Tests use local RSS XML fixtures rather than live feeds.

## Fragile Parts

The current ingestion layer is still early.

Known weak spots:

- RSS ingestion is synchronous; it should move to workers later.
- RSS skipped-item reasons are not preserved during parsing.
- Content hash dedupe may miss near-duplicates with rewritten headlines.
- There is no per-source rate limit or refresh interval yet.
- There is no `ETag` or `Last-Modified` cache handling yet.
- A single raw document currently creates one initial financial event, even though the schema supports one document producing many events.
- Ingestion job tracking is basic; enrichment jobs are not queued yet.

## Next Architecture Step

Day 8 should introduce queue and worker fundamentals. After that, ingestion should evolve toward:

```text
API receives source item
        |
        v
store RawDocument
        |
        v
queue enrichment JobRun
        |
        v
worker creates/enriches FinancialEvent records
```

That shift will make the system more production-shaped and prevent slow AI or parsing work from blocking request/response flows.
