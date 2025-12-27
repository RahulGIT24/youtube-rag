from redis import Redis
from core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)

async def get_redis()->Redis:
    return redis_client