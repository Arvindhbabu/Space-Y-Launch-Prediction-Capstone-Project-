"""
SpaceY Intelligence - Structured Logging Configuration
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "spacey", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a structured logger for SpaceY modules."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
