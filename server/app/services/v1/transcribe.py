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
from app.utils.llm import LLM
import json

llm = LLM()
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
                    limit=15,
                    score_threshold=0.5,
                ),
                models.Prefetch(
                    query=embeddings, 
                    using="dense-text",
                    limit=15,
                    score_threshold=0.5,
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
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=10
        )

        context=[]

        for point in res.points:
            payload=point.payload
            context.append({
                'start':payload['start'],
                'text':payload['text'],
                'score':point.score
            })
        
        res = llm.call_llm(context=json.dumps(context),query=query)
        raw_content = res.choices[0].message.content
        return JSONResponse(content={"message":"Query Successfully","data":json.loads(raw_content)},status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail="Internal Server Error")

def get_user_sessions(user_id:int,db:Session):
    try:
        results = db.query(
            UserToVideos.id.label("session_id"),
            UserToVideos.created_at,
            Video.video_id,
            Video.video_url,
            Video.ready,
            Video.processing,
            Video.enqueued,
        ).join(
            Video, UserToVideos.video_id == Video.video_id
        ).filter(
            UserToVideos.user_id == user_id
        ).all()

        if not results:
            return []

        return [dict(row._asdict()) for row in results]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail="Internal Server Error")

def get_user_session(user_id:int,db:Session,session_id:int):
    try:
        result = db.query(
            UserToVideos.id.label("session_id"),
            UserToVideos.created_at,
            Video.video_id,
            Video.video_url,
            Video.ready,
            Video.processing,
            Video.enqueued,
        ).join(
            Video, UserToVideos.video_id == Video.video_id
        ).filter(
            UserToVideos.user_id == user_id, UserToVideos.id==session_id
        ).first()

        if not result:
            raise HTTPException(detail="Session Not Found",status_code=404)

        res_dict = result._asdict()

        if res_dict['processing'] == False and res_dict['ready']==True:
            return res_dict
        raise HTTPException(detail="Video is not ready yet.",status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Internal Server Error")