from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import feedparser
import httpx

from api.app.core.config import settings
from api.app.core.logging import get_logger

logger = get_logger('signal_engine')


@dataclass
class RawSignal:
    source: str
    title: str
    body: str
    author: str | None
    url: str
    created_at_source: datetime | None


def _parse_rss_feeds(urls: Iterable[str]) -> list[RawSignal]:
    signals: list[RawSignal] = []
    for url in urls:
        feed = feedparser.parse(url)
        for item in feed.entries[:25]:
            published = None
            if getattr(item, 'published_parsed', None):
                published = datetime(*item.published_parsed[:6], tzinfo=timezone.utc)
            signals.append(
                RawSignal(
                    source=url,
                    title=getattr(item, 'title', ''),
                    body=getattr(item, 'summary', ''),
                    author=getattr(item, 'author', None),
                    url=getattr(item, 'link', ''),
                    created_at_source=published,
                )
            )
    return signals


def _pull_hn_hiring_posts() -> list[RawSignal]:
    # Uses official public Firebase API (real data).
    max_url = settings.hackernews_max_items_url
    signals: list[RawSignal] = []
    with httpx.Client(timeout=15.0) as client:
        max_item = client.get(max_url).json()
        for item_id in range(max_item, max_item - 50, -1):
            item = client.get(f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json').json()
            if not item:
                continue
            title = item.get('title', '')
            text = item.get('text', '') or ''
            if 'hiring' in title.lower() or 'need' in text.lower() or 'for hire' in text.lower():
                created = datetime.fromtimestamp(item['time'], tz=timezone.utc)
                signals.append(
                    RawSignal(
                        source='hackernews',
                        title=title,
                        body=text,
                        author=item.get('by'),
                        url=f"https://news.ycombinator.com/item?id={item_id}",
                        created_at_source=created,
                    )
                )
    return signals


def ingest_real_signals() -> list[RawSignal]:
    rss_urls = [u.strip() for u in settings.rsshub_urls.split(',') if u.strip()]
    rss_signals = _parse_rss_feeds(rss_urls)
    hn_signals = _pull_hn_hiring_posts()
    merged = rss_signals + hn_signals
    logger.info('signals_ingested', count=len(merged), rss=len(rss_signals), hackernews=len(hn_signals))
    return merged
