import logging

from configs.config import APP_CONFIG

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "custom": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "custom",
            "level": APP_CONFIG.log_level
        }
    },
    "loggers": {
        "api": {
            "handlers": ["console"],
            "level": APP_CONFIG.log_level,
            "propagate": True
        }
    }
}

logging.config.dictConfig(LOGGER_CONFIG)
LOGGER = logging.getLogger('api')
