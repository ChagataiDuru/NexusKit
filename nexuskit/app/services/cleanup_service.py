import os
import shutil
import time
import logging

TEMP_DIR = "/var/tmp/nexuskit_data"
GRACE_PERIOD_SECONDS = 3600  # 1 hour

logger = logging.getLogger(__name__)

def setup_temp_directory():
    os.makedirs(TEMP_DIR, exist_ok=True)
    logger.info(f"Ensured temporary directory exists: {TEMP_DIR}")

def schedule_cleanup(task_id: str):
    task_dir = os.path.join(TEMP_DIR, task_id)
    if os.path.exists(task_dir):
        logger.info(f"Scheduling cleanup for task {task_id} in {GRACE_PERIOD_SECONDS} seconds.")
        # In a real-world scenario, this would use a proper task queue/scheduler
        # For now, we'll just log and rely on the cron job for robustness.
        # The actual deletion will be handled by the cron job.

def cleanup_task_directory(task_id: str):
    task_dir = os.path.join(TEMP_DIR, task_id)
    if os.path.exists(task_dir):
        try:
            shutil.rmtree(task_dir)
            logger.info(f"Cleaned up task directory: {task_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up task directory {task_dir}: {e}")

def periodic_cleanup_script(age_seconds: int = 86400):  # 24 hours
    setup_temp_directory()
    now = time.time()
    for item in os.listdir(TEMP_DIR):
        item_path = os.path.join(TEMP_DIR, item)
        if os.path.isdir(item_path):
            try:
                # Check modification time of the directory
                mod_time = os.path.getmtime(item_path)
                if (now - mod_time) > age_seconds:
                    shutil.rmtree(item_path)
                    logger.info(f"Cron job cleaned up old task directory: {item_path}")
            except Exception as e:
                logger.error(f"Cron job error cleaning up {item_path}: {e}")

