import os
import json
import redis
import time
import pickle
import pandas as pd
from datetime import datetime, timedelta
import random
# Load Redis environment variables
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_DB = os.environ.get('REDIS_DB', 0)

# Create a Redis connection pool
default_redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB
)

class SessionStore:
    def __init__(self, redis_pool=None):
        self.redis = redis.Redis(connection_pool=default_redis_pool or redis_pool)
        self.cache = {}

    def _get_date_key(self):
        return datetime.now().strftime("%Y-%m-%d")

    def _get_random_recs_key(self):
        return f'random_recs:{self._get_date_key()}'

    def _get_sample_taken_key(self):
        return f'sample_taken:{self._get_date_key()}'


    def set_prev_rec(self, key, track_ids, recommended_songs):
        start_time = time.time()
        data = {'track_ids': track_ids, 'recommended_ids': recommended_songs}
        self.redis.set(key, json.dumps(data), ex=86400, nx=True) # 1 day
        self.redis.set(key, json.dumps(data), xx=True)
        self.cache[key] = data
        print("Time to set rec ids in redis:", time.time() - start_time)


    def set_random_recs(self, recommended_songs):
        if self.redis.exists(self._get_sample_taken_key()):
            print('Sample already taken, no random recs saved')
            return

        pipe = self.redis.pipeline()
        pipe.rpush(self._get_random_recs_key(), *recommended_songs)
        pipe.expire(self._get_random_recs_key(), 86400, nx=True) # 1 day
        pipe.expire(self._get_sample_taken_key(), 86400, nx=True) # 1 day
        pipe.execute()

    def get_random_recs(self):
        random_rec_key = self._get_random_recs_key()
        sample_taken_key = self._get_sample_taken_key()

        list_length = self.redis.llen(random_rec_key)
        print("List length", list_length)

        if list_length == 10 and self.redis.exists(sample_taken_key):  
            print("Returning existing daily sample")
            return [item.decode('utf-8') for item in self.redis.lrange(random_rec_key, 0, -1)]


        if list_length < 200 and not self.redis.exists(sample_taken_key):
            print("Not enough items for a sample")
            return None


        # 10 Random indices
        random_indicies = random.sample(range(list_length), 10)
        pipe = self.redis.pipeline()
        for index in random_indicies:
            pipe.lindex(random_rec_key, index)
        
        sample = [item.decode('utf-8') for item in pipe.execute() if item is not None]

        if not sample:
            print("Sample empty")
            return None
         
        pipe = self.redis.pipeline()
        pipe.delete(random_rec_key)
        pipe.rpush(random_rec_key, *sample)
        pipe.set(sample_taken_key, 1)
        pipe.expire(sample_taken_key, 86400) # 1 day
        pipe.expire(random_rec_key, 86400) # 1 day
        pipe.execute()
    
        print("Sample taken and replaced original data")
        return sample
        

    
    def set_vector(self, key, vector, ttl=3600):
        if isinstance(vector, pd.DataFrame):
            serialized_vector = pickle.dumps(vector)
        else:
            serialized_vector = json.dumps(vector)
        self.redis.set(key, serialized_vector)
        self.redis.expire(key, ttl)
        self.cache[key] = vector


    def set_user_top_data(self, key, data):
        self.redis.set(key, json.dumps(data), ex=86400)
        self.cache[key] = data
        print("Cache size", len(self.cache))

        # cached_data = self.get_data_cache(key) 
        # if cached_data is not None and cached_data == data:
        #     print("Data is cached")
        # else:
        #     print("Data is not cached")

    def update_total_recs(self, num_recs: int):
        key = 'total_recs'
        hourly_key = f'hourly_recs:{datetime.now().strftime("%Y-%m-%d:%H")}'
        print("Hourly key", hourly_key)

        pipeline = self.redis.pipeline()
        pipeline.incrby(key, num_recs)
        pipeline.incrby(hourly_key, num_recs)
        pipeline.expire(hourly_key, 3600, nx=True)
        pipeline.execute()

    
    def get_total_recs(self):
        key = 'total_recs'
        total_recs = self.redis.get(key)
        # print("Total recs", int(total_recs.decode('utf-8')))  
        current_hour = datetime.now().strftime("%Y-%m-%d:%H")
        key = f'hourly_recs:{current_hour}'
        hourly_recs = self.redis.get(key)
        decoded_total_recs = int(total_recs.decode('utf-8')) if total_recs else 0
        decoded_hourly_recs = int(hourly_recs.decode('utf-8')) if hourly_recs else 0
        return decoded_total_recs, decoded_hourly_recs
      

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
        user_key_pattern = f"{unique_id}:*"
        cursor = "0"
        total_deleted = 0

        while cursor != 0:
            print(f'Starting scan with cursor: {cursor}')
            cursor, keys = self.redis.scan(cursor=cursor, match=user_key_pattern)

            deleted_count = 0
            if keys:
                # Delete from Redis
                deleted_count = self.redis.delete(*keys)
                total_deleted += deleted_count

                # Remove from in-memory cache
                for key in keys:
                    key_str = key.decode('utf-8')
                    if key_str in self.cache:
                        del self.cache[key_str]
                        print(f'Removed key from cache: {key_str}')

            print(f'Count of keys deleted: {deleted_count}')

        print(f'Total count of keys deleted: {total_deleted}')
        print(f'Cache size after clearing: {len(self.cache)}')
            

    # def clear_user_cache(self, unique_id):
    #     print(f'Clearing cache for user: {unique_id}')
    #     user_key_pattern = f"{unique_id}:*"  # Adjust the naming convention if needed
    #     cursor = "0"
    #     keys_to_delete = []

    #     # Scan the in-memory cache for keys associated with the user
    #     while cursor != 0:
    #         print(f'Starting scan with cursor: {cursor}')
    #         cursor, keys = self.redis.scan(cursor=cursor, match=user_key_pattern, count=1000)
    #         print(f'Cursor after scan: {cursor}')
    #         print(f'Number of keys found: {len(keys)}')

    #         keys_to_delete.extend(key.decode() for key in keys if key.decode() in self.cache)
    #         print(f'Number of keys to delete: {len(keys_to_delete)}')

    #     # Remove the keys from the in-memory cache
    #     for key in keys_to_delete:
    #         self.cache.pop(key)
    #         print(f'Removed key from cache: {key}')

    #     print(f'Cache size after clearing user cache: {len(self.cache)}')
    #     return


    def clear_all(self):
        self.cache.clear()
        self.redis.flushdb()


    def print_all_keys(self):
        for key in self.redis.scan_iter():
            print(f'Key: {key}')
            # data_str = self.redis.get(key)
            # if data_str:
            #     data = json.loads(data_str)
            #     #, Data: {data}'

    def get_memory_usage(self, key):
        return self.redis.memory_usage(key) 


### For Testing
    def set_total_recs(self, num_recs: int): # For Testing
        key = 'total_recs'
        self.redis.set(key, json.dumps(num_recs))

    # def delete_keys(self):
    #     key1 = f'sample_taken:{self._get_date_key()}'
    #     key2 = f'random_recs:{self._get_date_key()}'    
    #     self.redis.delete(key1, key2)