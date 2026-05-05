"""
services/weather.py — Fetch current weather from OpenWeatherMap.

Docs: https://openweathermap.org/current
"""

from __future__ import annotations
from dataclasses import dataclass
import requests
from config import cfg
from utils.logger import get_logger

logger = get_logger(__name__)

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


@dataclass
class WeatherData:
    city: str
    country: str
    summary: str          # e.g. "Partly cloudy"
    description: str      # longer description
    temp_c: float
    feels_like_c: float
    temp_min_c: float
    temp_max_c: float
    humidity: int         # %
    wind_speed: float     # m/s
    icon_code: str        # e.g. "02d"
    forecast: list[ForecastSlot]

    @property
    def icon_url(self) -> str:
        return f"https://openweathermap.org/img/wn/{self.icon_code}@2x.png"


@dataclass
class ForecastSlot:
    dt_txt: str
    temp_c: float
    summary: str
    icon_code: str


class WeatherService:
    def __init__(self):
        self._key = cfg.openweather_api_key
        self._city = cfg.openweather_city
        self._units = cfg.openweather_units

    @retry(times=3, delay=2)
    def fetch(self) -> WeatherData:
        params = {"q": self._city, "appid": self._key, "units": self._units}

        # Current conditions
        resp = requests.get(CURRENT_URL, params=params, timeout=10)
        resp.raise_for_status()
        cur = resp.json()

        # 3-day forecast (next 6 slots = ~18 hours)
        fresp = requests.get(FORECAST_URL, params={**params, "cnt": 6}, timeout=10)
        fresp.raise_for_status()
        fdata = fresp.json()

        forecast = [
            ForecastSlot(
                dt_txt=slot["dt_txt"],
                temp_c=slot["main"]["temp"],
                summary=slot["weather"][0]["main"],
                icon_code=slot["weather"][0]["icon"],
            )
            for slot in fdata.get("list", [])
        ]

        return WeatherData(
            city=cur["name"],
            country=cur["sys"]["country"],
            summary=cur["weather"][0]["main"],
            description=cur["weather"][0]["description"].capitalize(),
            temp_c=cur["main"]["temp"],
            feels_like_c=cur["main"]["feels_like"],
            temp_min_c=cur["main"]["temp_min"],
            temp_max_c=cur["main"]["temp_max"],
            humidity=cur["main"]["humidity"],
            wind_speed=cur["wind"]["speed"],
            icon_code=cur["weather"][0]["icon"],
            forecast=forecast,
        )
