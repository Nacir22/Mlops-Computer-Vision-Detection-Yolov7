"""
Central logging configuration for the ISD project.

`from isd.logger import logging` gives a logger that writes BOTH:
  - to a timestamped file under logs/  (a permanent record of every run)
  - to the console (stdout)            (so you can follow the pipeline live)

Use logging instead of print() everywhere:
    logging.info("...")     normal progress
    logging.warning("...")  something odd but not fatal
    logging.error("...")    an error was caught
"""

import logging
import os
import sys
from datetime import datetime

from from_root import from_root

# One log file per run, e.g. 07_10_2026_14_30_05.log
LOG_FILE: str = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Folder that holds the log FILES. We create the FOLDER (logs/), not a folder
# named after the log file — that was the previous bug.
LOG_DIR: str = os.path.join(from_root(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH: str = os.path.join(LOG_DIR, LOG_FILE)

LOG_FORMAT: str = "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),   # persistent record on disk
        logging.StreamHandler(sys.stdout),    # live output in the terminal
    ],
)
