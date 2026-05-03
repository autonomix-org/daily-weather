"""
briefing_agent.py — Orchestrates all data services and composes the briefing.

Flow:
    fetch weather → fetch news → fetch calendar → (optional AI summary)
    → render HTML email → send
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from config import cfg
from services.weather import WeatherService, WeatherData
from services.news import NewsService, Article
from services.calendar import CalendarService, CalendarEvent
from services.email_sender import EmailSender
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BriefingContext:
    """All data collected for today's briefing."""
    date: date
    weather: WeatherData | None = None
    articles: list[Article] = field(default_factory=list)
    events: list[CalendarEvent] = field(default_factory=list)
    ai_narrative: str | None = None


class BriefingAgent:
    """Top-level agent that coordinates services and sends the email."""

    def __init__(self):
        self.weather_svc = WeatherService()
        self.news_svc = NewsService()
        self.calendar_svc = CalendarService()
        self.email_sender = EmailSender()

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Fetch all data, compose briefing, and send email."""
        ctx = self._collect(BriefingContext(date=date.today()))
        if cfg.enable_ai_summary:
            ctx.ai_narrative = self._generate_narrative(ctx)
        self.email_sender.send(ctx)
        logger.info("Briefing dispatched for %s", ctx.date)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _collect(self, ctx: BriefingContext) -> BriefingContext:
        """Fetch from each service; failures are logged but non-fatal."""
        try:
            ctx.weather = self.weather_svc.fetch()
            logger.info("Weather fetched: %s", ctx.weather.summary)
        except Exception as e:
            logger.warning("Weather fetch failed: %s", e)

        try:
            ctx.articles = self.news_svc.fetch()
            logger.info("News fetched: %d articles", len(ctx.articles))
        except Exception as e:
            logger.warning("News fetch failed: %s", e)

        try:
            ctx.events = self.calendar_svc.fetch_today()
            logger.info("Calendar fetched: %d events", len(ctx.events))
        except Exception as e:
            logger.warning("Calendar fetch failed: %s", e)

        return ctx

    def _generate_narrative(self, ctx: BriefingContext) -> str | None:
        """Optional: ask Claude to write a friendly narrative summary."""
        if not cfg.anthropic_api_key:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)

            prompt_lines = [
                f"Today is {ctx.date.strftime('%A, %B %d %Y')}.",
            ]
            if ctx.weather:
                prompt_lines.append(
                    f"Weather in {cfg.openweather_city}: {ctx.weather.summary}, "
                    f"{ctx.weather.temp_c:.0f}°C, humidity {ctx.weather.humidity}%."
                )
            if ctx.articles:
                headlines = "; ".join(a.title for a in ctx.articles[:3])
                prompt_lines.append(f"Top headlines: {headlines}.")
            if ctx.events:
                event_titles = "; ".join(e.title for e in ctx.events)
                prompt_lines.append(f"Calendar events: {event_titles}.")

            prompt_lines.append(
                "Write a friendly, concise 2-3 sentence morning briefing narrative "
                "based on the above. Be warm and conversational."
            )

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=256,
                messages=[{"role": "user", "content": "\n".join(prompt_lines)}],
            )
            return message.content[0].text
        except Exception as e:
            logger.warning("AI narrative generation failed: %s", e)
            return None
