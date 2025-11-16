"""
Custom logger with Rich library for beautiful console output.
"""

import logging
import os
import sys
import warnings
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Suppress all LangChain deprecation warnings immediately on import
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*deprecated.*")
warnings.filterwarnings("ignore", message=".*DeprecationWarning.*")
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
warnings.filterwarnings("ignore", category=FutureWarning, module="langchain")
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Suppress warnings at the environment level
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

# Disable LangChain verbose output
os.environ["LANGCHAIN_VERBOSE"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


# Define a custom theme for the logger
custom_theme = Theme(
    {
        "logging.level.debug": "dim blue",
        "logging.level.info": "bright_blue",
        "logging.level.warning": "yellow",
        "logging.level.error": "bold red",
        "logging.level.critical": "bold red blink",
    }
)


def setup_logger(
    name: str = "langchat",
    level: int = logging.INFO,
    console: Optional[Console] = None,
    show_path: bool = False,
    rich_tracebacks: bool = True,
) -> logging.Logger:
    """
    Setup a logger with Rich formatting.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        console: Optional Rich Console instance
        show_path: Show file path in logs (default: False for cleaner output)
        rich_tracebacks: Enable rich tracebacks (default: True)

    Returns:
        Configured logger instance
    """
    # Create console if not provided
    if console is None:
        console = Console(theme=custom_theme, stderr=bool(sys.stderr.isatty()))

    # Create Rich handler with clean formatting
    handler = RichHandler(
        console=console,
        show_time=False,  # Hide time for cleaner output
        show_path=False,  # Hide path for cleaner output
        rich_tracebacks=rich_tracebacks,
        tracebacks_show_locals=False,
        markup=True,
        show_level=True,
        log_time_format="",
    )

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Add Rich handler
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def configure_logging():
    """
    Configure global logging settings:
    - Suppress httpx and urllib3 logs
    - Suppress LangChain deprecation warnings
    - Setup root logger with Rich handler
    """
    # Suppress httpx and urllib3 verbose logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Disable LangChain verbose logging
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain.chains").setLevel(logging.WARNING)
    logging.getLogger("langchain.callbacks").setLevel(logging.WARNING)

    # Warnings are already suppressed at module level
    # This is just for completeness
    pass

    # Setup root logger for all langchat modules
    root_logger = logging.getLogger("langchat")
    if not root_logger.handlers:
        handler = RichHandler(
            console=Console(theme=custom_theme),
            show_time=False,  # Hide time for cleaner output
            show_path=False,  # Hide path for cleaner output
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            markup=True,
            show_level=True,
            log_time_format="",
        )
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        root_logger.propagate = False


# Configure logging on import
configure_logging()

# Create the default logger instance
logger = setup_logger()

__all__ = ["logger", "setup_logger", "configure_logging"]
