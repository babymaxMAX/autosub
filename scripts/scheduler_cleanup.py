"""Scheduled cleanup task for storage."""
import os
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings
from scripts.cleanup_storage import cleanup_old_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_scheduled_cleanup():
    """Run cleanup on schedule (can be called by cron or as a service)."""
    # Cleanup based on tier TTL settings
    try:
        result = cleanup_old_files(
            hours=settings.CLEANUP_HOURS,
            min_free_space_gb=5.0
        )
        if result:
            logger.info(f"Cleanup completed: {result['deleted_count']} dirs deleted, {result['freed_space_mb']:.2f} MB freed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)


if __name__ == "__main__":
    # For cron usage, just run once
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        logger.info("Running cleanup once...")
        run_scheduled_cleanup()
        logger.info("Cleanup completed")
    else:
        # Run as a service (check every hour, cleanup every 24 hours)
        logger.info("Starting cleanup scheduler (runs every 24 hours)...")
        last_run = 0
        cleanup_interval = 24 * 3600  # 24 hours in seconds
        
        # Run immediately on start
        run_scheduled_cleanup()
        last_run = time.time()
        
        # Then run on schedule
        while True:
            current_time = time.time()
            if current_time - last_run >= cleanup_interval:
                run_scheduled_cleanup()
                last_run = current_time
            time.sleep(3600)  # Check every hour

