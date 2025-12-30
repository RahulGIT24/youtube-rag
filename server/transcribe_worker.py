import json
from core.redis import redis_client
from workers.utils.transcript import Transcript
from core.qdrant import get_client
from workers.utils.embedding_models import dense_embedding,sparse_embedding
from dotenv import load_dotenv
import os
import uuid
from sqlalchemy.orm import Session
import logging
from qdrant_client import models
from models.video import Video
from core.database import get_session

logging.basicConfig(filename="transcribe_worker.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',
                    level=logging.INFO)
load_dotenv()

obj = Transcript()
qdrant_client=get_client()
db:Session=get_session()

QUEUE_NAME="queue:pending"
COLLECTION_NAME=os.getenv('QDRANT_COLLECTION')

def process_job(job: dict):
    db:Session = list(get_session())[0]
    try:
        video_id = job["video_id"]

        video = (
            db.query(Video)
            .filter(
                Video.video_id == video_id,
                Video.processing == False,
                Video.ready == False
            )
            .with_for_update()
            .first()
        )

        if not video:
            return

        video.processing = True
        db.commit()

        logging.info(f"Processing video {video_id}")

        chunks = obj.fetch_transcript(video_id=video_id)
        texts = [c["text"] for c in chunks]

        embeddings = list(dense_embedding.embed(texts))
        sparse_embeddings = list(sparse_embedding.embed(texts))

        points = []

        for chunk, dense, sparse in zip(chunks, embeddings, sparse_embeddings):
            point_id = uuid.uuid4()

            points.append(
                models.PointStruct(
                    id=point_id,
                    payload={
                        "video_id": video_id,
                        "start": chunk["start"],
                        "text": chunk["text"]
                    },
                    vector={
                        "dense-text": dense,
                        "sparse-text": models.SparseVector(
                            indices=sparse.indices.tolist(),
                            values=sparse.values.tolist()
                        )
                    }
                )
            )

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        video.processing = False
        video.ready = True
        db.commit()

        logging.info(f"Finished video {video_id}")

    except Exception:
        db.rollback()
        logging.exception("Error processing video")

    finally:
        db.close()


def start_worker():
    print("Worker Started")
    logging.info("Waiting For Jobs......")

    while True:
        try:
            _,data=redis_client.blpop(QUEUE_NAME)
            job = json.loads(data)
            process_job(job)

        except Exception as e:
            logging.exception('Error while processing jobs. '+e)

if __name__ == "__main__":
    start_worker()