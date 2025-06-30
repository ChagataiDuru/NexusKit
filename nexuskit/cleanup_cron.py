import sys
import os

# Add the parent directory to the Python path to allow importing app.services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from services import cleanup_service
import logging

# Configure logging for the cleanup script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/cleanup.log") # Separate log file for cleanup
    ]
)

if __name__ == "__main__":
    logging.info("Starting periodic cleanup script...")
    cleanup_service.periodic_cleanup_script()
    logging.info("Periodic cleanup script finished.")
