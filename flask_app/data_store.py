import os
import json
import redis

# Load Redis environment variables
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_DB = os.environ.get('REDIS_DB', 0)

# Create a Redis connection pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB
)

class DataStore:
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis_pool)

    def set_data(self, key, track_ids, recommended_songs):
        data = {'track_ids': track_ids, 'recommended_songs': recommended_songs}
        self.redis.set(key, json.dumps(data))

    def get_data(self, key):
        data_str = self.redis.get(key)
        if data_str:
            data = json.loads(data_str)
            return data
        return None

    def remove_data(self, key):
        self.redis.delete(key)