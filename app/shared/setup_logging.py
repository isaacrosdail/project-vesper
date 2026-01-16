from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask

import logging.config

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s",
        }
    },
    "handlers": {  # dictates where logs go (console, file, etc.)
        "stdout": {
            "class": "logging.StreamHandler",  # prints to console
            "formatter": "simple",  # references formatter above
            "stream": "ext://sys.stderr",  # ext:// means "external" ie "this is a variable that's defined outside of this config"
        }
    },
    "loggers": {"werkzeug": {"level": "WARNING"}, "alembic": {"level": "WARNING"}},
    "root": {"level": "DEBUG", "handlers": ["stdout"]},
}


def setup_logging(app: Flask) -> None:
    """Configure logging based on app config"""
    config = LOGGING_CONFIG.copy()
    config["root"]["level"] = app.config["LOGGING_LEVEL"]
    logging.config.dictConfig(config=config)

    # Silence some 3rd party
    logging.getLogger("urllib3").setLevel(logging.WARNING)
