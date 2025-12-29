import json
from utils.redis_instance import redis_client
from utils.transcript import Transcript
from utils.qdrant import get_client
from utils.embedding_models import dense_embedding,sparse_embedding
from dotenv import load_dotenv
import os
import logging
import uuid
from qdrant_client import models

logging.basicConfig(filename="transcribe_worker.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',
                    level=logging.INFO)
load_dotenv()

obj = Transcript()
qdrant_client=get_client()

QUEUE_NAME="queue:pending"
COLLECTION_NAME=os.getenv('QDRANT_COLLECTION')

def process_job(job:dict):
    try:
        video_id=job['video_id']

        if not video_id:
            raise ValueError("Video Id not found")

        exists = qdrant_client.scroll(COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="video_id",
                        match=models.MatchValue(value=video_id),
                    ),
                ],
            )
        )

        if(len(exists)>0):
            logging.info("Already Stored. Skipping Processing for video id " + video_id)
            return


        logging.info("Processing Video ID "+video_id)

        chunks = obj.fetch_transcript(video_id=video_id)

        texts = [chunk['text'] for chunk in chunks]
        embeddings = list(dense_embedding.embed(texts))
        sparse_embeddings = list(sparse_embedding.embed(texts))

        points=[]

        for (chunk,dense,sparse) in zip(chunks,embeddings,sparse_embeddings):

            points.append(models.PointStruct(
                id=uuid.uuid4(),
                payload={
                    "start": chunk["start"],
                    "text": chunk["text"],
                    "video_id":video_id
                },
                vector={
                    "dense-text": dense,
                    "sparse-text": models.SparseVector(
                        indices=sparse.indices.tolist(),
                        values=sparse.values.tolist()
                    )
                }
            ))

        qdrant_client.upsert(collection_name=COLLECTION_NAME,points=points)
        logging.info("Processed Video Id -> "+video_id)
    except Exception as e:
        raise e

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