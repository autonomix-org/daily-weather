"""
services/news.py — Fetch top headlines from NewsAPI.

Docs: https://newsapi.org/docs/endpoints/top-headlines
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import requests
from config import cfg
from utils.logger import get_logger

logger = get_logger(__name__)

TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"


@dataclass
class Article:
    title: str
    description: Optional[str]
    url: str
    source: str
    published_at: str
    image_url: Optional[str] = None


class NewsService:
    def __init__(self):
        self._key = cfg.news_api_key
        self._topics = cfg.news_topics
        self._country = cfg.news_country
        self._max = cfg.news_max_articles

    def fetch(self) -> list[Article]:
        """Fetch top articles across all configured topics (deduplicated)."""
        seen_urls: set[str] = set()
        articles: list[Article] = []

        for topic in self._topics:
            if len(articles) >= self._max:
                break
            try:
                batch = self._fetch_topic(topic, seen_urls)
                articles.extend(batch)
            except Exception as e:
                logger.warning("Failed fetching news for topic '%s': %s", topic, e)

        return articles[: self._max]

    def _fetch_topic(self, topic: str, seen: set[str]) -> list[Article]:
        params = {
            "apiKey": self._key,
            "q": topic,
            "country": self._country,
            "pageSize": self._max,
            "language": "en",
        }
        resp = requests.get(TOP_HEADLINES_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for raw in data.get("articles", []):
            url = raw.get("url", "")
            if url in seen or not raw.get("title"):
                continue
            seen.add(url)
            results.append(
                Article(
                    title=raw["title"],
                    description=raw.get("description"),
                    url=url,
                    source=raw.get("source", {}).get("name", "Unknown"),
                    published_at=raw.get("publishedAt", ""),
                    image_url=raw.get("urlToImage"),
                )
            )
        return results
