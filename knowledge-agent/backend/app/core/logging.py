"""
Application-wide structured logger.
"""

import logging
import sys


def setup_logger(name: str = "knowledge_agent", level: int = logging.INFO) -> logging.Logger:
    """Create and return a configured logger with structured formatting."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()
