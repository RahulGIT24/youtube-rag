from fastapi import FastAPI,Depends, HTTPException
from app.api.router import api_router
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from core.config import settings
from core.async_redis import redis_client
from core.qdrant import create_collection
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.utils.get_current_user import get_current_user

@asynccontextmanager
async def lifespan(app:FastAPI):
    await FastAPILimiter.init(redis_client)
    create_collection()
    yield
    await FastAPILimiter.close()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/',dependencies=[Depends(RateLimiter(times=2,seconds=5))])
def health_check():
    return {"message":"Server is healthy"}

@app.get('/api/v1/get_current_user',dependencies=[Depends(RateLimiter(times=4,seconds=1))],)
async def signup(user=Depends(get_current_user)):
    try:
        data={
            "name":user.name,
            "email":user.email,
            "id":user.id
        }

        return JSONResponse(content=data,status_code=200)

    except Exception as e:
        raise HTTPException(detail="Internal Server Error",status_code=500)

app.include_router(api_router,prefix=settings.API_V1_PREFIX,dependencies=[Depends(RateLimiter(times=10,seconds=5))])