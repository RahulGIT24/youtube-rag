from fastapi import APIRouter,HTTPException
from fastapi.responses import JSONResponse
from schemas.transcribe import TranscribeBody
from utils.urls import extract_youtube_video_id
from services.v1.transcribe import generate_transcribe_and_push_to_redis

router = APIRouter()

@router.post('/')
def generate_video_transcription_and_timestamps(payload:TranscribeBody):
    video_url = payload.video_url
    video_id = extract_youtube_video_id(video_url)

    if video_id==None:
        raise HTTPException(detail="Invalid Video URL",status_code=400)

    res = generate_transcribe_and_push_to_redis(user_id='1',video_id=video_id,video_url=video_url)

    if res:
        return JSONResponse(content={"message":"Video URL Submitted For Processing"},status_code=202)
    else:
        raise HTTPException(detail="Internal Server Error",status_code=500)
