"""Application logging for the source-based renovated build."""

from __future__ import annotations

import logging
from pathlib import Path


LOG_PATH = Path(__file__).resolve().parent / "logs" / "app.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("agrifarm")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(handler)
