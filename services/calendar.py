"""
services/calendar.py — Fetch today's events from Google Calendar.

Auth: Service account (credentials.json) OR OAuth2 flow.
Docs: https://developers.google.com/calendar/api/v3/reference/events/list
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date, timezone
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import cfg
from utils.logger import get_logger

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


@dataclass
class CalendarEvent:
    title: str
    start: str          # ISO-8601
    end: str            # ISO-8601
    location: Optional[str]
    description: Optional[str]
    is_all_day: bool

    @property
    def start_time_str(self) -> str:
        if self.is_all_day:
            return "All day"
        try:
            dt = datetime.fromisoformat(self.start)
            return dt.strftime("%I:%M %p")
        except ValueError:
            return self.start


class CalendarService:
    def __init__(self):
        self._creds_path = cfg.google_credentials_json
        self._calendar_id = cfg.google_calendar_id

    def fetch_today(self) -> list[CalendarEvent]:
        service = self._build_service()
        today = date.today()

        time_min = datetime(today.year, today.month, today.day, tzinfo=timezone.utc).isoformat()
        time_max = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc).isoformat()

        result = (
            service.events()
            .list(
                calendarId=self._calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for item in result.get("items", []):
            start = item["start"]
            end = item["end"]
            is_all_day = "date" in start and "dateTime" not in start
            events.append(
                CalendarEvent(
                    title=item.get("summary", "(No title)"),
                    start=start.get("dateTime") or start.get("date", ""),
                    end=end.get("dateTime") or end.get("date", ""),
                    location=item.get("location"),
                    description=item.get("description"),
                    is_all_day=is_all_day,
                )
            )
        return events

    def _build_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self._creds_path, scopes=SCOPES
        )
        return build("calendar", "v3", credentials=creds)
