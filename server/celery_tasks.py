from celery import Celery
from datetime import timedelta
from dotenv import load_dotenv
import os
from core.database import get_session
from datetime import datetime
from models.video import Video
from redis import Redis
from dotenv import load_dotenv
import os
import logging
import json

logging.basicConfig(filename="celery_worker.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',
                    level=logging.INFO)

load_dotenv()
QUEUE_NAME="queue:pending"
REDIS_PORT=os.getenv('REDIS_PORT')
REDIS_HOST=os.getenv('REDIS_HOST')


redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)

celery_app = Celery("tasks", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
STUCK_AFTER = timedelta(minutes=20)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(300.0, requeue_stuck_videos.s(), name="Requeue every 5 min")

# celery -A celery_tasks worker --beat --loglevel=info

MAX_RETRIES = 5
@celery_app.task
def requeue_stuck_videos():
    logging.info("Starting requeue_stuck_videos task")
    try:
        db = next(get_session())
        now = datetime.utcnow()
        cutoff = now - STUCK_AFTER

        stuck_videos = (
            db.query(Video)
            .filter(
                Video.enqueued==True,
                Video.processing==False,
                Video.ready==False,
                Video.enqueued_at < cutoff,
            )
            .all()
        )

        logging.info(f"Found {len(stuck_videos)} stuck videos to requeue")

        for video in stuck_videos:
            if video.error_msg != None:
                continue
            if video.retries >= MAX_RETRIES:
                video.enqueued = False
                video.error_msg = f"Max retries ({MAX_RETRIES}) exceeded"
                logging.info(f"Video {video.video_id} marked as failed")
                continue

            video.enqueued_at = now
            video.retries += 1

            redis_client.lpush(
                QUEUE_NAME,
                json.dumps({
                    "video_id": video.video_id,
                    "video_url": video.video_url
                })
            )

            logging.info(f"Requeued video {video.video_id}")

    except Exception as e:
        logging.exception(f"Error in requeue_stuck_videos task: {e}")