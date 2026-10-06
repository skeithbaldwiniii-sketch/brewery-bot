import logging
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "data" / "logs"
LOG_FILE = LOG_DIR / "monthly_sales.log"
PYTHON = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"
RUNNER = PROJECT_DIR / "monthly_sales.py"


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


def main():
    configure_logging()

    logging.info("Starting monthly sales dry run.")
    logging.info("Project directory: %s", PROJECT_DIR)
    logging.info("Python executable: %s", PYTHON)
    logging.info("Runner: %s", RUNNER)

    result = subprocess.run(
        [str(PYTHON), str(RUNNER), "--download"],
        cwd=PROJECT_DIR,
        check=False,
    )

    if result.returncode == 0:
        logging.info("Monthly sales dry run completed successfully.")
    else:
        logging.error(
            "Monthly sales dry run failed with exit code %s.",
            result.returncode,
        )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

