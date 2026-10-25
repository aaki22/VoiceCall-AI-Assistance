import logging

from src.logging.config import configure_logging


def test_configure_logging_sets_level():
    configure_logging("WARNING")

    assert logging.getLogger().level == logging.WARNING
