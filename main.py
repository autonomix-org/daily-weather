"""
main.py — Entry point for the Daily Briefing Agent.

Usage:
    python main.py          # Start scheduler (daemon mode)
    python main.py --now    # Send briefing immediately and exit
"""

import argparse
import sys
from utils.logger import get_logger
from agents.briefing_agent import BriefingAgent
from scheduler.cron import start_scheduler

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Daily Briefing Agent")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Send briefing immediately instead of waiting for scheduled time",
    )
    args = parser.parse_args()

    agent = BriefingAgent()

    if args.now:
        logger.info("Running briefing immediately (--now flag)")
        try:
            agent.run()
            logger.info("Briefing sent successfully ✓")
        except Exception as e:
            logger.error(f"Briefing failed: {e}")
            sys.exit(1)
    else:
        logger.info("Starting scheduler…")
        start_scheduler(agent)


if __name__ == "__main__":
    main()
