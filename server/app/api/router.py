from fastapi import APIRouter
from app.api.v1 import transcribe,auth,query

api_router = APIRouter()

api_router.include_router(transcribe.router,prefix='/transcribe',tags=['transcibe'])
api_router.include_router(auth.router,prefix='/auth',tags=['auth'])
api_router.include_router(query.router,prefix='/query',tags=['query'])