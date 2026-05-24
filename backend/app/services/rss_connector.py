from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
import re
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class RssItem:
    title: str
    body: str
    source_url: str | None
    published_at: datetime | None


@dataclass(frozen=True)
class RssFeed:
    source_name: str
    items: list[RssItem]


def fetch_rss_xml(feed_url: str, timeout_seconds: int) -> str:
    request = Request(
        feed_url,
        headers={"User-Agent": "FinanceEngine/0.1 (+local-development)"},
    )

    with urlopen(request, timeout=timeout_seconds) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def parse_rss_xml(xml_text: str, fallback_source_name: str = "rss") -> RssFeed:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
        
    if channel is None:
        raise ValueError("RSS feed is missing a channel element")

    source_name = _text(channel, "title") or fallback_source_name
    items = [
        item
        for item_node in channel.findall("item")
        if (item := _parse_item(item_node)) is not None
    ]

    return RssFeed(source_name=source_name, items=items)


def _parse_item(item_node: ET.Element) -> RssItem | None:
    title = _text(item_node, "title")
    description = _text(item_node, "description")
    source_url = _text(item_node, "link") or _text(item_node, "guid")
    published_at = _parse_datetime(_text(item_node, "pubDate"))

    if not title or not description:
        return None

    return RssItem(
        title=_clean_text(title),
        body=_clean_text(description),
        source_url=source_url,
        published_at=published_at,
    )


def _text(parent: ET.Element, tag: str) -> str | None:
    child = parent.find(tag)
    if child is None or child.text is None:
        return None
    return child.text.strip()


def _clean_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(without_tags)).strip()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
