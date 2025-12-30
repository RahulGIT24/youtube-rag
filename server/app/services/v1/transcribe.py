from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json

from app.models.video import Video
from app.models.user_to_videos import UserToVideos
from app.core.redis import redis_client

QUEUE_NAME = "queue:pending"

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
                enqueued=True
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
