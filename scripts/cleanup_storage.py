"""Cleanup old files from storage."""
import os
import sys
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_disk_usage(path: Path) -> dict:
    """Get disk usage information."""
    import shutil
    total, used, free = shutil.disk_usage(path)
    return {
        "total": total,
        "used": used,
        "free": free,
        "percent_used": (used / total) * 100 if total > 0 else 0
    }


def cleanup_old_files(hours: int = 24, min_free_space_gb: float = 5.0):
    """Clean up files older than specified hours and check disk space."""
    storage_path = Path(settings.STORAGE_PATH)
    
    if not storage_path.exists():
        logger.warning(f"Storage path does not exist: {storage_path}")
        return
    
    # Check disk space
    disk_info = get_disk_usage(storage_path)
    free_gb = disk_info["free"] / (1024 ** 3)
    logger.info(f"Disk usage: {disk_info['percent_used']:.1f}% used, {free_gb:.2f} GB free")
    
    # If disk is running low, be more aggressive
    if free_gb < min_free_space_gb:
        logger.warning(f"Low disk space ({free_gb:.2f} GB), using more aggressive cleanup")
        # Clean files older than 12 hours if disk is low
        hours = min(hours, 12)
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    deleted_count = 0
    freed_space = 0
    
    logger.info(f"Cleaning up files older than {hours} hours...")
    logger.info(f"Cutoff time: {cutoff_time}")
    
    # Clean task directories (task_*)
    for task_dir in storage_path.iterdir():
        if not task_dir.is_dir():
            continue
        
        # Skip model cache directories
        if task_dir.name.startswith('.') or task_dir.name == 'models':
            continue
        
        # Check directory modification time
        try:
            dir_mtime = datetime.fromtimestamp(task_dir.stat().st_mtime)
        except OSError:
            logger.warning(f"Cannot access {task_dir.name}, skipping")
            continue
        
        if dir_mtime < cutoff_time:
            try:
                # Calculate directory size
                dir_size = sum(f.stat().st_size for f in task_dir.rglob('*') if f.is_file())
                
                # Remove directory
                shutil.rmtree(task_dir)
                
                deleted_count += 1
                freed_space += dir_size
                
                logger.info(f"✓ Deleted: {task_dir.name} ({dir_size / 1024 / 1024:.2f} MB)")
            except Exception as e:
                logger.error(f"✗ Error deleting {task_dir.name}: {e}", exc_info=True)
    
    logger.info(f"\nCleanup complete:")
    logger.info(f"  Deleted directories: {deleted_count}")
    logger.info(f"  Freed space: {freed_space / 1024 / 1024:.2f} MB")
    
    # Log final disk usage
    disk_info_after = get_disk_usage(storage_path)
    free_gb_after = disk_info_after["free"] / (1024 ** 3)
    logger.info(f"Disk usage after cleanup: {disk_info_after['percent_used']:.1f}% used, {free_gb_after:.2f} GB free")
    
    return {
        "deleted_count": deleted_count,
        "freed_space_mb": freed_space / 1024 / 1024,
        "free_space_gb": free_gb_after
    }


if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else settings.CLEANUP_HOURS
    min_free = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    cleanup_old_files(hours, min_free)

