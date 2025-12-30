from pydantic import BaseModel

class TranscribeBody(BaseModel):
    video_url:str

class UserQuery(BaseModel):
    query:str