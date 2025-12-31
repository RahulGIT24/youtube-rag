from fastapi import APIRouter,HTTPException,Depends
from core.database import get_session
from app.schemas.transcribe import TranscribeBody
from app.utils.urls import extract_youtube_video_id
from app.services.v1.transcribe import generate_transcribe_and_push_to_redis,get_user_sessions,get_user_session
from sqlalchemy.orm import Session
from app.utils.get_current_user import get_current_user
from models.user_to_videos import UserToVideos
from models.video import Video

router = APIRouter()

@router.post('/')
def generate_video_transcription_and_timestamps(payload:TranscribeBody,user=Depends(get_current_user),db:Session=Depends(get_session)):
    video_url = payload.video_url
    video_id = extract_youtube_video_id(video_url)

    if video_url==None or video_id==None:
        raise HTTPException(detail="Invalid Video URL",status_code=400)

    return generate_transcribe_and_push_to_redis(user_id=int(user.id),video_id=video_id,video_url=video_url,db=db)

@router.get('/get-sessions')
def get_user_session_videos(db:Session=Depends(get_session),user=Depends(get_current_user)):
    return get_user_sessions(db=db,user_id=user.id)

@router.get('/session')
def get_session(session_id:int,db:Session=Depends(get_session),user=Depends(get_current_user)):
    return get_user_session(session_id=session_id,db=db,user_id=user.id)