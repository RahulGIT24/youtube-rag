from core.redis import redis_client
import json

def generate_transcribe_and_push_to_redis(user_id,video_id,video_url):
    try:
        data = {
        "user_id":user_id,"video_id":video_id,"video_url":video_url
        }
        # Flush to Database

        # Push to redis queue
        # json.dumps(data)
        redis_client.lpush('queue:pending',json.dumps(data))
        return True
    except Exception as e:
        print(e)
        return False