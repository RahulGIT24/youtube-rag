import json
from utils.redis_instance import redis_client
from utils.transcript import Transcript
from utils.qdrant import get_client
from utils.embedding_models import dense_embedding
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

obj = Transcript()
qdrant_client=get_client()

QUEUE_NAME="queue:pending"

def process_job(job:dict):
    try:
        video_id=job['video_id']

        print("Processing Video ID "+video_id)

        chunks = obj.fetch_transcript(video_id=video_id)

        texts = [chunk['text'] for chunk in chunks]
        embeddings = list(dense_embedding.embed(texts))

        points=[]

        for (chunk,vector) in zip(chunks,embeddings):
            points.append({
                    "id":uuid.uuid4(),
                    "vector":vector,
                    "payload":{
                    "start": chunk["start"],
                    "text": chunk["text"],
                    "video_id":video_id
                }
            })

        qdrant_client.upsert(collection_name=os.getenv('QDRANT_COLLECTION'),points=points)
        print("Processed Video Id -> "+video_id)
    except Exception as e:
        raise e

def start_worker():
    print("Worker Started")

    while True:
        print("Waiting For Jobs......")
        try:
            _,data=redis_client.blpop(QUEUE_NAME)
            job = json.loads(data)
            process_job(job)

        except Exception as e:
            print('Error while processing jobs. ',e)

if __name__ == "__main__":
    start_worker()