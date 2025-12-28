from fastapi import FastAPI,Depends
import uvicorn
from api.router import api_router
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from core.config import settings
from core.async_redis import redis_client
from core.qdrant import create_collection
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

if __name__ == "__main__":
    uvicorn.run(host='127.0.0.1',port=8001,app='main:app',reload=True)