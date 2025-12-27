from pydantic import BaseModel

class TranscribeBody(BaseModel):
    video_url:str