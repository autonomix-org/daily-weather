"""
scheduler/cron.py — APScheduler-based daily job runner.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from config import cfg
from utils.logger import get_logger

logger = get_logger(__name__)


def start_scheduler(agent) -> None:
    """Start blocking scheduler; runs agent.run() every morning."""
    scheduler = BlockingScheduler(timezone="local")

    scheduler.add_job(
        func=_run_with_error_handling,
        args=[agent],
        trigger="cron",
        hour=cfg.briefing_hour,
        minute=cfg.briefing_minute,
        id="daily_briefing",
        name="Daily Briefing Agent",
        replace_existing=True,
    )

    logger.info(
        "Scheduler started — briefing will fire daily at %s", cfg.briefing_time
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


def _run_with_error_handling(agent) -> None:
    try:
        agent.run()
    except Exception as e:
        logger.error("Briefing job failed: %s", e, exc_info=True)
