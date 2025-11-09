"""Logging configuration for the application."""
import logging
import sys


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance with consistent formatting.

    Args:
        name: Logger name (usually __name__ from calling module).
        level: Logging level (default: INFO).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (usually __name__ from calling module).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
