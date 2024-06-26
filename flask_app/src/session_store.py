import os
import json
import redis
import time
import pickle
import pandas as pd
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
        start_time = time.time()
        data = {'track_ids': track_ids, 'recommended_ids': recommended_songs}
        print("Time to set rec ids in redis:", time.time() - start_time)
        self.redis.set(key, json.dumps(data))
        self.cache[key] = data

    def set_vector(self, key, vector, ttl=3600):
        if isinstance(vector, pd.DataFrame):
            serialized_vector = pickle.dumps(vector)
        else:
            serialized_vector = json.dumps(vector)
        self.redis.set(key, serialized_vector)
        self.redis.expire(key, ttl)
        self.cache[key] = vector


    def set_user_top_data(self, key, data):
        self.redis.set(key, json.dumps(data))
        self.cache[key] = data
        print("Cache size", len(self.cache))

        cached_data = self.get_data_cache(key) 
        if cached_data is not None and cached_data == data:
            print("Data is cached")
        else:
            print("Data is not cached")

    def get_data(self, key): 
        start_time = time.time()
        if key in self.cache:
            print(f'Cache hit time for {key}: {time.time() - start_time}')
            return self.cache[key]

        print(f'Cache miss for key: {key}')
        data_str = self.redis.get(key)

        if data_str:
            try:
                data = pickle.loads(data_str)
                print(f'Pickle load time for {key}: {time.time() - start_time}')
            except (pickle.UnpicklingError, EOFError):
                data = json.loads(data_str)
                print(f'Json load time for {key}: {time.time() - start_time}')

            self.cache[key] = data
            return data
        
        return None

    def remove_user_data(self, unique_id):
        if unique_id is None:
            print('No unique_id found in the session')
            return
        print(f'Removing data associated with user: {unique_id}')
        user_key_pattern = f"{unique_id}*"
        cursor = "0"
        total_deleted = 0  # To count the number of keys deleted

        while cursor != "0":
            print(f'Cursor: {cursor}')
            cursor, keys = self.redis.scan(cursor=cursor, match=user_key_pattern)
            print(f'Cursor: {cursor}')
            print(f'Keys: {keys}')
            if keys:
                with self.redis.pipeline() as pipe:
                    for key in keys:
                        pipe.delete(key)
                    deleted_count = pipe.execute()
                total_deleted += sum(deleted_count)  # Update the count of deleted keys

                print(f'Count of keys associated with user deleted: {total_deleted}')
            else:
                print('No keys found')

        print('Count of keys associated with user deleted', total_deleted)
        return
        

    def clear_user_cache(self, unique_id):
        print(f'Clearing cache for user: {unique_id}')
        user_key_pattern = f"{unique_id}*"  # Adjust the naming convention if needed
        cursor = "0"
        keys_to_delete = []

        # Scan the in-memory cache for keys associated with the user
        while cursor != 0:
            print(f'Starting scan with cursor: {cursor}')
            cursor, keys = self.redis.scan(cursor=cursor, match=user_key_pattern, count=1000)
            print(f'Cursor after scan: {cursor}')
            print(f'Number of keys found: {len(keys)}')

            keys_to_delete.extend(key.decode() for key in keys if key.decode() in self.cache)
            print(f'Number of keys to delete: {len(keys_to_delete)}')

        # Remove the keys from the in-memory cache
        for key in keys_to_delete:
            self.cache.pop(key)
            print(f'Removed key from cache: {key}')

        print(f'Cache size after clearing user cache: {len(self.cache)}')
        return


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