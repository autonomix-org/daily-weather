"""
services/email_sender.py — Render and send the HTML briefing email via SMTP.
"""

from __future__ import annotations
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from config import cfg
from utils.logger import get_logger

logger = get_logger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class EmailSender:
    def __init__(self):
        self._host = cfg.smtp_host
        self._port = cfg.smtp_port
        self._user = cfg.smtp_user
        self._password = cfg.smtp_password
        self._recipient = cfg.email_recipient
        self._subject = cfg.email_subject
        self._jinja = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    def send(self, ctx) -> None:
        """Render template and send email."""
        html_body = self._render(ctx)
        msg = self._build_message(html_body)
        self._dispatch(msg)

    def _render(self, ctx) -> str:
        template = self._jinja.get_template("email_template.html")
        return template.render(
            date=ctx.date,
            weather=ctx.weather,
            articles=ctx.articles,
            events=ctx.events,
            ai_narrative=ctx.ai_narrative,
            city=cfg.openweather_city,
        )

    def _build_message(self, html_body: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self._subject
        msg["From"] = self._user
        msg["To"] = self._recipient
        msg.attach(MIMEText(html_body, "html"))
        return msg

    def _dispatch(self, msg: MIMEMultipart) -> None:
        with smtplib.SMTP(self._host, self._port) as server:
            server.ehlo()
            server.starttls()
            server.login(self._user, self._password)
            server.sendmail(self._user, self._recipient, msg.as_string())
            logger.info("Email sent to %s", self._recipient)
