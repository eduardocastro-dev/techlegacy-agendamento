import logging
import os
from logging.config import dictConfig

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def configure_logging():
    """Configura o logging da aplicação."""

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    if log_level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"LOG_LEVEL inválido: {log_level}. "
            f"Valores aceitos: {', '.join(sorted(VALID_LOG_LEVELS))}"
        )

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": ("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "standard",
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
        }
    )

    logging.getLogger(__name__).info(
        "Logging configurado. Nível: %s",
        log_level,
    )
