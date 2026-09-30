"""Logging configuration that keeps MCP stdout clean."""

import logging
import sys


_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(level: str) -> None:
    """Configure application logs on stderr, never on the MCP stdout stream."""
    logging.basicConfig(
        level=getattr(logging, level),
        format=_LOG_FORMAT,
        stream=sys.stderr,
        force=True,
    )
