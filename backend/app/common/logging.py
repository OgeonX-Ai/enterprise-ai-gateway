import logging
from typing import Optional


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] [correlation_id=%(correlation_id)s] %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(format=LOG_FORMAT, level=level)


def get_logger(name: str) -> logging.LoggerAdapter:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logging.LoggerAdapter(logger, {"correlation_id": "-"})


def bind_correlation_id(logger: logging.LoggerAdapter, correlation_id: Optional[str]) -> logging.LoggerAdapter:
    logger.extra["correlation_id"] = correlation_id or "-"
    return logger
