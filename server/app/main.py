from fastapi import FastAPI,Depends
from app.api.router import api_router
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app.core.config import settings
from app.core.async_redis import redis_client
from app.core.qdrant import create_collection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    await FastAPILimiter.init(redis_client)
    create_collection()
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

@app.get('/',dependencies=[Depends(RateLimiter(times=2,seconds=5))])
def health_check():
    return {"message":"Server is healthy"}

app.include_router(api_router,prefix=settings.API_V1_PREFIX,dependencies=[Depends(RateLimiter(times=2,seconds=5))])