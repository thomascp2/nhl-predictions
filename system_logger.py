"""
Structured logging system for NHL betting system

Usage:
    from system_logger import get_logger

    logger = get_logger(__name__)
    logger.info("Starting prediction generation")
    logger.warning("Low confidence prediction")
    logger.error("Failed to fetch data")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name: str, level=logging.INFO):
    """
    Get a configured logger instance

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if no handlers exist (avoid duplicates)
    if not logger.handlers:
        logger.setLevel(level)

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # File handler (daily log file)
        today = datetime.now().strftime('%Y-%m-%d')
        file_handler = logging.FileHandler(
            LOG_DIR / f"system_{today}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets everything

        # Error file handler (errors only)
        error_handler = logging.FileHandler(
            LOG_DIR / f"errors_{today}.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

    return logger


def log_workflow_start(workflow_name: str):
    """Log the start of a workflow"""
    logger = get_logger("workflow")
    logger.info("="*80)
    logger.info(f"STARTING WORKFLOW: {workflow_name}")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    logger.info("="*80)


def log_workflow_end(workflow_name: str, success: bool, duration_seconds: float = None):
    """Log the end of a workflow"""
    logger = get_logger("workflow")
    status = "SUCCESS" if success else "FAILED"
    logger.info("="*80)
    logger.info(f"WORKFLOW {status}: {workflow_name}")
    if duration_seconds:
        logger.info(f"Duration: {duration_seconds:.1f} seconds")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    logger.info("="*80)


def log_step(step_name: str, status: str, details: str = None):
    """
    Log a workflow step

    Args:
        step_name: Name of the step
        status: 'start', 'success', 'warning', 'error'
        details: Optional details message
    """
    logger = get_logger("workflow")

    if status == 'start':
        logger.info(f"[STEP] {step_name}")
        if details:
            logger.info(f"  {details}")
    elif status == 'success':
        logger.info(f"[SUCCESS] {step_name}")
        if details:
            logger.info(f"  {details}")
    elif status == 'warning':
        logger.warning(f"[WARNING] {step_name}")
        if details:
            logger.warning(f"  {details}")
    elif status == 'error':
        logger.error(f"[ERROR] {step_name}")
        if details:
            logger.error(f"  {details}")


# Example usage and testing
if __name__ == "__main__":
    print("Testing structured logging system...")
    print()

    # Create test logger
    logger = get_logger("test_module")

    # Test different log levels
    logger.debug("This is a debug message (only in file)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test workflow logging
    log_workflow_start("Test Workflow")
    log_step("Fetch data", "start", "Connecting to NHL API...")
    log_step("Fetch data", "success", "Fetched 157 player stats")
    log_step("Generate predictions", "start")
    log_step("Generate predictions", "warning", "Low confidence for some players")
    log_workflow_end("Test Workflow", success=True, duration_seconds=12.5)

    print()
    print("="*60)
    print("Logs saved to:")
    print(f"  - logs/system_{datetime.now().strftime('%Y-%m-%d')}.log")
    print(f"  - logs/errors_{datetime.now().strftime('%Y-%m-%d')}.log")
    print("="*60)
