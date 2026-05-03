"""
config.py — load and validate all environment variables in one place.
Access anywhere: from config import cfg
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Weather
    openweather_api_key: str = field(default_factory=lambda: os.environ["OPENWEATHER_API_KEY"])
    openweather_city: str = field(default_factory=lambda: os.getenv("OPENWEATHER_CITY", "London,GB"))
    openweather_units: str = field(default_factory=lambda: os.getenv("OPENWEATHER_UNITS", "metric"))

    # News
    news_api_key: str = field(default_factory=lambda: os.environ["NEWS_API_KEY"])
    news_topics: list[str] = field(default_factory=lambda: os.getenv("NEWS_TOPICS", "technology").split(","))
    news_country: str = field(default_factory=lambda: os.getenv("NEWS_COUNTRY", "us"))
    news_max_articles: int = field(default_factory=lambda: int(os.getenv("NEWS_MAX_ARTICLES", "5")))

    # Google Calendar
    google_credentials_json: str = field(default_factory=lambda: os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json"))
    google_calendar_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CALENDAR_ID", "primary"))

    # Email
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = field(default_factory=lambda: os.environ["SMTP_USER"])
    smtp_password: str = field(default_factory=lambda: os.environ["SMTP_PASSWORD"])
    email_recipient: str = field(default_factory=lambda: os.environ["EMAIL_RECIPIENT"])
    email_subject: str = field(default_factory=lambda: os.getenv("EMAIL_SUBJECT", "☀️ Your Daily Briefing"))

    # Scheduler
    briefing_time: str = field(default_factory=lambda: os.getenv("BRIEFING_TIME", "07:00"))

    # AI (optional)
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    enable_ai_summary: bool = field(default_factory=lambda: os.getenv("ENABLE_AI_SUMMARY", "false").lower() == "true")

    @property
    def briefing_hour(self) -> int:
        return int(self.briefing_time.split(":")[0])

    @property
    def briefing_minute(self) -> int:
        return int(self.briefing_time.split(":")[1])

    def validate(self) -> None:
        missing = []
        for key in ["openweather_api_key", "news_api_key", "smtp_user", "smtp_password", "email_recipient"]:
            if not getattr(self, key, None):
                missing.append(key.upper())
        if missing:
            raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")


cfg = Config()
