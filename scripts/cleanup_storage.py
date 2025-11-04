"""Cleanup old files from storage."""
import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings


def cleanup_old_files(hours: int = 24):
    """Clean up files older than specified hours."""
    storage_path = Path(settings.STORAGE_PATH)
    
    if not storage_path.exists():
        print(f"Storage path does not exist: {storage_path}")
        return
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    deleted_count = 0
    freed_space = 0
    
    print(f"Cleaning up files older than {hours} hours...")
    print(f"Cutoff time: {cutoff_time}")
    
    for task_dir in storage_path.iterdir():
        if not task_dir.is_dir():
            continue
        
        # Check directory modification time
        dir_mtime = datetime.fromtimestamp(task_dir.stat().st_mtime)
        
        if dir_mtime < cutoff_time:
            try:
                # Calculate directory size
                dir_size = sum(f.stat().st_size for f in task_dir.rglob('*') if f.is_file())
                
                # Remove directory
                shutil.rmtree(task_dir)
                
                deleted_count += 1
                freed_space += dir_size
                
                print(f"✓ Deleted: {task_dir.name} ({dir_size / 1024 / 1024:.2f} MB)")
            except Exception as e:
                print(f"✗ Error deleting {task_dir.name}: {e}")
    
    print(f"\nCleanup complete:")
    print(f"  Deleted directories: {deleted_count}")
    print(f"  Freed space: {freed_space / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else settings.CLEANUP_HOURS
    cleanup_old_files(hours)

