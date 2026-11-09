"""ASTRA-Sec Structured Logging Configuration."""

import json
import logging
import sys
from typing import Any, Dict


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as structured single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "node_eid"):
            log_payload["node_eid"] = record.node_eid
        if hasattr(record, "bundle_id"):
            log_payload["bundle_id"] = record.bundle_id
        return json.dumps(log_payload)


def configure_logging(level: str = "INFO", json_output: bool = False) -> logging.Logger:
    """Configures the root ASTRA-Sec logger.

    Args:
        level: Minimum log level string (e.g. DEBUG, INFO, WARNING, ERROR).
        json_output: If True, formats output as JSON lines; otherwise standard text.

    Returns:
        The configured 'astra_sec' logger instance.
    """
    logger = logging.getLogger("astra_sec")
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers on re-configuration
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if json_output:
            handler.setFormatter(StructuredJsonFormatter())
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%SZ",
            )
            handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger
