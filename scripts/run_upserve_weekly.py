import logging
from pathlib import Path

from integrations.upserve import process_latest_upserve_report
from knowledge.database import initialize_database


LOG_DIR = Path("data/logs")
LOG_FILE = LOG_DIR / "upserve_weekly.log"


def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.WARNING)


def main():
    configure_logging()

    logging.info("Starting Upserve weekly report processing.")

    try:
        initialize_database()

        result = process_latest_upserve_report()

        logging.info(
            "Upserve processing status: %s",
            result["status"],
        )
        logging.info(
            "Reporting period: %s",
            result["reporting_period"],
        )

        if result["status"] == "processed":
            logging.info(
                "Slack timestamp: %s",
                result["slack_timestamp"],
            )
        else:
            logging.info(
                "Report was already processed. "
                "No Slack message sent."
            )

        return result

    except Exception:
        logging.exception(
            "Upserve weekly report processing failed."
        )
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit(1)
