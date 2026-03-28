import redis
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL=os.getenv("REDIS_URL")

redis_conn = redis.Redis.from_url(REDIS_URL,decode_responses=True)
