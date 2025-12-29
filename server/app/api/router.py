from fastapi import APIRouter
from app.api.v1 import transcribe,auth

api_router = APIRouter()

api_router.include_router(transcribe.router,prefix='/transcribe',tags=['transcibe'])
api_router.include_router(auth.router,prefix='/auth',tags=['auth'])