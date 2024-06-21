import os
import json
import redis
import time
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

class SessionStore:
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis_pool)
        self.cache = {}

    def set_prev_rec(self, key, track_ids, recommended_songs):
        data = {'track_ids': track_ids, 'recommended_ids': recommended_songs}
        self.redis.set(key, json.dumps(data))
        self.cache[key] = data

    
    def set_user_top_data(self, key, data):
        self.redis.set(key, json.dumps(data))
        self.cache[key] = data

    def get_data_json(self, key):
        data_str = self.redis.get(key) 
        if data_str:
            data = json.loads(data_str)
            return data
        
        return None
    def get_data_cache(self, key): 
        if key in self.cache:
            print(f'Cache hit for key: {key}')
            return self.cache[key]
        print(f'Cache miss for key: {key}')
        return None
    def remove_user_data(self, unique_id):
        user_key_pattern = f"{unique_id}*"
        cursor = "0"
        while cursor != 0:
            cursor, keys = self.redis.scan(cursor=cursor, match=user_key_pattern)
            if keys:
                with self.redis.pipeline() as pipe:
                    for key in keys:
                        pipe.delete(key)
                    pipe.execute()
        print('Count of keys associated with user deleted', len(keys))
        
        

    def clear_user_cache(self, unique_id):
        print("Cache", self.cache)
        user_key_pattern = f"{unique_id}*"
        cursor = "0"
        keys_to_delete = []

        # Scan the in-memory cache for keys associated with the user
        while cursor != 0:
            cursor, keys = self.redis.scan(cursor=cursor, match=user_key_pattern, count=10000)
            keys_to_delete.extend(key for key in keys if key in self.cache)

        # Remove the keys from the in-memory cache
        for key in keys_to_delete:
            self.cache.pop(key)

    def clear_all(self):
        self.cache.clear()
        self.redis.flushdb()


    def print_all_data(self):
        for key in self.redis.scan_iter():
            data_str = self.redis.get(key)
            if data_str:
                data = json.loads(data_str)
                print(f'Key: {key}, Data: {data}')

    def get_memory_usage(self, key):
        return self.redis.memory_usage(key) 