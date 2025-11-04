"""Worker main entry point."""
import logging
from redis import Redis
from rq import Worker, Queue
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start RQ worker."""
    logger.info("Starting AutoSub Worker...")
    
    # Connect to Redis
    redis_conn = Redis.from_url(settings.redis_url)
    
    # Create queues
    queues = [
        Queue("video_processing", connection=redis_conn),
    ]
    
    # Start worker
    worker = Worker(queues, connection=redis_conn)
    logger.info("Worker started successfully!")
    worker.work()


if __name__ == "__main__":
    main()

