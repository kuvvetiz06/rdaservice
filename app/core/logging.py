import logging
from logging.config import dictConfig


LOG_LEVEL = logging.getLevelName("INFO")


def configure_logging() -> None:
    """Configure a simple logging setup for the application."""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": LOG_LEVEL,
            }
        },
        "root": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
    }
    dictConfig(logging_config)
