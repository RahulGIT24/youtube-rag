from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    decode_responses=True,
)