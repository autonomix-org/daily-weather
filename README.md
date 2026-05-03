# Daily Briefing Agent 🌤️

A morning briefing agent that fetches **weather**, **top news**, and **calendar events**, then sends a beautifully formatted summary email — every day, automatically.

---

## Features

- 🌦️ **Weather** — current conditions + daily forecast via OpenWeatherMap
- 📰 **News** — top headlines by topic/country via NewsAPI
- 📅 **Calendar** — today's events from Google Calendar
- 📧 **Email** — HTML summary email via SMTP or SendGrid
- ⏰ **Scheduler** — runs automatically at a configured time each morning
- 🤖 **AI Summary** — optional Claude-powered narrative briefing via Anthropic API

---

## Project Structure

```
daily-weather/
├── main.py                  # Entry point — run directly or via scheduler
├── config.py                # All config loaded from environment
├── requirements.txt
├── .env.example
│
├── agents/
│   └── briefing_agent.py    # Orchestrates all services → builds briefing
│
├── services/
│   ├── weather.py           # OpenWeatherMap API
│   ├── news.py              # NewsAPI
│   ├── calendar.py          # Google Calendar API
│   └── email_sender.py      # SMTP / SendGrid email dispatch
│
├── scheduler/
│   └── cron.py              # APScheduler daily job
│
├── templates/
│   └── email_template.html  # Jinja2 HTML email template
│
└── utils/
    └── logger.py            # Structured logging
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/autonomix-org/daily-weather.git
cd daily-weather
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys and settings
```

### 3. Run once (immediate send)

```bash
python main.py --now
```

### 4. Run on schedule (daemon mode)

```bash
python main.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key |
| `OPENWEATHER_CITY` | City name (e.g. `Thrissur,IN`) |
| `NEWS_API_KEY` | NewsAPI.org key |
| `NEWS_TOPICS` | Comma-separated topics (e.g. `technology,science`) |
| `GOOGLE_CREDENTIALS_JSON` | Path to Google service account JSON |
| `GOOGLE_CALENDAR_ID` | Calendar ID (usually your email) |
| `SMTP_HOST` | SMTP server host |
| `SMTP_PORT` | SMTP port (default `587`) |
| `SMTP_USER` | SMTP username / email |
| `SMTP_PASSWORD` | SMTP password or app password |
| `EMAIL_RECIPIENT` | Where to send the briefing |
| `BRIEFING_TIME` | Cron time (e.g. `07:00`) |
| `ANTHROPIC_API_KEY` | (Optional) Claude AI narrative summary |

---

## API Keys You'll Need

| Service | Free Tier | Link |
|---|---|---|
| OpenWeatherMap | 1000 calls/day | https://openweathermap.org/api |
| NewsAPI | 100 calls/day | https://newsapi.org |
| Google Calendar | Free | https://console.cloud.google.com |
| Anthropic (optional) | — | https://console.anthropic.com |

---

## License

MIT
