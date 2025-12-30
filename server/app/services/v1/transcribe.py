from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json
from datetime import datetime
from models.video import Video
from models.user_to_videos import UserToVideos
from core.redis import redis_client
from core.embedding_models import dense_embedding,sparse_embedding
from core.qdrant import get_client
from core.config import settings
from qdrant_client import models

QUEUE_NAME = "queue:pending"
qdrant_client=get_client()
COLLECTION_NAME=settings.QDRANT_COLLECTION

def generate_transcribe_and_push_to_redis(
    user_id: int,
    video_id: str,
    video_url: str,
    db: Session
):
    try:
        existing_session = (
            db.query(UserToVideos)
            .filter(
                UserToVideos.video_id == video_id,
                UserToVideos.user_id == user_id
            )
            .first()
        )

        if existing_session:
            return JSONResponse(
                content={
                    "message": "Video already submitted",
                    "session_id": existing_session.id
                },
                status_code=202
            )

        video = (
            db.execute(
                select(Video)
                .where(Video.video_id == video_id)
                .with_for_update()
            )
            .scalar_one_or_none()
        )

        if not video:
            video = Video(
                video_id=video_id,
                video_url=video_url,
                enqueued=True,
                enqueued_at=datetime.utcnow()
            )
            db.add(video)
            db.commit()

            redis_client.lpush(
                QUEUE_NAME,
                json.dumps({
                    "video_id": video_id,
                    "video_url": video_url
                })
            )

        elif not video.enqueued:
            video.enqueued = True
            video.enqueued_at=datetime.utcnow()
            db.commit()

            redis_client.lpush(
                QUEUE_NAME,
                json.dumps({
                    "video_id": video_id,
                    "video_url": video_url
                })
            )

        new_session = UserToVideos(
            session_name=video_url,
            video_id=video_id,
            user_id=user_id
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return JSONResponse(
            content={
                "message": "Video submitted for processing",
                "session_id": new_session.id
            },
            status_code=202
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

def generate_response(session_id:int,query:str,db:Session,user_id:int):
    try:
        exising_session=db.query(UserToVideos).filter(UserToVideos.id==session_id,UserToVideos.user_id==user_id).first()
        
        if not exising_session:
            raise HTTPException(status_code=404,detail="Session Not found")

        video_id = exising_session.video_id

        embeddings = list(dense_embedding.embed([query]))[0]
        sparse_embeddings = list(sparse_embedding.embed([query]))

        res = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(indices=sparse_embeddings[0].indices, values=sparse_embeddings[0].values),
                    using="sparse-text",
                    limit=20,
                    score_threshold=0.7,
                ),
                models.Prefetch(
                    query=embeddings, 
                    using="dense-text",
                    limit=20,
                    score_threshold=0.6,
                ),
            ],
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="video_id",
                        match=models.MatchValue(value=video_id)
                    )
                ]
            ),
            score_threshold=0.6,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=10
        )

        print(res)

        return JSONResponse(content={"message":"Queried Successfully"},status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Internal Server Error")