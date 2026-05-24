from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE_URL = "http://127.0.0.1:8000"
RSS_FEED_URL = "https://www.sec.gov/news/pressreleases.rss"


def post_json(path: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{path} failed with {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(
            f"Could not reach {API_BASE_URL}. Start the API before running this script.",
        ) from exc


def main() -> int:
    unique_suffix = datetime.now(UTC).isoformat()
    manual_payload = {
        "source_name": "smoke-test",
        "title": f"Smoke test AI infrastructure update {unique_suffix}",
        "body": (
            "Cloud providers increased AI infrastructure spending plans as demand "
            "for data center capacity continued to expand across major technology firms."
        ),
        "source_url": "smoke://manual-ingestion",
        "ingestion_metadata": {"test": "ingestion_smoke_check"},
    }

    first_status, first_manual = post_json("/ingest/manual", manual_payload)
    second_status, second_manual = post_json("/ingest/manual", manual_payload)

    if first_status != 201 or first_manual["status"] != "created":
        raise RuntimeError(f"Expected manual create, got {first_status}: {first_manual}")

    if second_status != 200 or second_manual["status"] != "duplicate":
        raise RuntimeError(
            f"Expected manual duplicate, got {second_status}: {second_manual}",
        )

    rss_status, rss_result = post_json(
        "/ingest/run",
        {
            "feed_url": RSS_FEED_URL,
            "source_name": "SEC Press Releases",
            "limit": 2,
        },
    )

    if rss_status != 200:
        raise RuntimeError(f"Expected RSS success, got {rss_status}: {rss_result}")

    if rss_result["fetched_count"] < 1 or len(rss_result["items"]) < 1:
        raise RuntimeError(f"Expected at least one RSS item, got: {rss_result}")

    print("Manual ingestion created:", first_manual["raw_document_id"])
    print("Manual duplicate returned:", second_manual["raw_document_id"])
    print(
        "RSS ingestion:",
        f"created={rss_result['created_count']}",
        f"duplicates={rss_result['duplicate_count']}",
        f"skipped={rss_result['skipped_count']}",
    )
    print("Ingestion smoke check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
