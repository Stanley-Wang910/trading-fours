import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))  
import pytest
import redis
import random 
import pandas
from collections import Counter
import string
from session_store import SessionStore
from datetime import datetime, timedelta
import time

@pytest.fixture(scope='module')
def local_redis_pool():
    """Create a Redis connection pool for testing"""
    return redis.ConnectionPool(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        password=os.environ.get('REDIS_PASSWORD'),
        db=int(os.environ.get('REDIS_DB', 0))
    )

@pytest.fixture(scope='module')
def session_store(local_redis_pool):
    """Create a SessionStore instance using the local Redis pool"""
    return SessionStore(redis_pool=local_redis_pool)

# # Optional: Add a fixture to clear Redis before/after tests if needed
# @pytest.fixture(autouse=True)
# def clear_redis(session_store):
#     yield
#     session_store.redis.flushdb()  # Clear Redis after each test

def test_update_trending_genres(session_store):
    session_store.redis.delete(f"genre_ratios:{datetime.now().strftime('%Y-%W')}")
    initial_counts = {'Electronic': 100, 'Rock': 50, 'Jazz': 25}
    session_store.update_trending_genres(initial_counts)

    retrieved_counts = session_store.get_trending_genres()
    assert retrieved_counts == {b'Electronic': b'100', b'Rock': b'50', b'Jazz': b'25'}

    # Tet incremental update
    additional_counts = {'Electronic': 50, 'Rock': 25, 'Pop': 75}
    session_store.update_trending_genres(additional_counts)
    
    updated_counts = session_store.get_trending_genres()
    assert updated_counts == {b'Electronic': b'150', b'Rock': b'75', b'Jazz': b'25', b'Pop': b'75'}

def test_expiration_and_updates(session_store):
    session_store.redis.delete(f"genre_ratios:{datetime.now().strftime('%Y-%W')}")
    key = f"genre_ratios:{datetime.now().strftime('%Y-%W')}"

    # Set initial counts
    initial_counts = {'Electronic': 100, 'Rock': 50}
    session_store.update_trending_genres(initial_counts)
    
    # Check initial TTL
    initial_ttl = session_store.redis.ttl(key)
    assert 0 < initial_ttl <= timedelta(days=7).total_seconds()
    
    # Wait for a short time
    time.sleep(2)
    
    # Update counts
    session_store.update_trending_genres({'Pop': 75})
    
    # Check TTL after update
    updated_ttl = session_store.redis.ttl(key)
    assert 0 < updated_ttl < initial_ttl, "TTL should have decreased but not reset"
    
    # Ensure counts are correct
    final_counts = session_store.get_trending_genres()
    assert final_counts == {b'Electronic': b'100', b'Rock': b'50', b'Pop': b'75'}

def test_weekly_reset(session_store, monkeypatch):

    keys_to_delete = session_store.redis.keys("genre_ratios:*")
    if keys_to_delete:
        session_store.redis.delete(*keys_to_delete)
    # Set initial counts
    initial_counts = {'Electronic': 100, 'Rock': 50}
    session_store.update_trending_genres(initial_counts)
    

    # Initial Key
    initial_key = f"genre_ratios:{datetime.now().strftime('%Y-%W')}"

    # Mock the datetime to simulate a week passing
    class MockDatetime:
        @classmethod
        def now(cls):
            return datetime.now() + timedelta(days=9) 

    monkeypatch.setattr('session_store.datetime', MockDatetime)


    # Add new counts (should be in a new key)
    new_counts = {'Pop': 75, 'Jazz': 25}
    session_store.update_trending_genres(new_counts)



    # Check that we have two separate keys
    all_keys = session_store.redis.keys("genre_ratios:*")
    assert len(all_keys) == 2

    # Check initial key has expired

    # Check that the new key has only the new genres
    current_counts = session_store.get_trending_genres()
    assert current_counts == {b'Pop': b'75', b'Jazz': b'25'}

    # Verify new key has different name
    new_key = all_keys[0].decode()
    assert new_key != initial_key, "Expected new key to have different name"





# Testing setting daily recommendation sampling
# def generate_random_song_id():
#     """Generate a random song ID prefixed with the user ID for easy identification."""
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=22))

#     # return random.choice(pandas.read_csv('session_store_random.csv')['track_id'])

# def test_multi_user_random_recs(session_store):
#     # Clear any existing data
#     session_store.redis.flushdb()

#     num_users = 20
#     songs_per_user = 15
    
#     for user in range(num_users):
#         user_songs = [generate_random_song_id() for _ in range(songs_per_user)]
#         session_store.set_random_recs(user_songs)

#         # Check total recommendations
#         total_recs = session_store.redis.llen(session_store._get_random_recs_key())

#         if user < 13:
#             assert total_recs == (user+1) * songs_per_user, f"Expected {(user+1) * songs_per_user} recommendations, but got {total_recs}"
#         else:
#             # Test initial sampling
#             recs = session_store.get_random_recs()
#             assert recs is not None, "Expected recommendations, but got None"
#             assert len(recs) == 10, f"Expected 10 recommendations, but got {len(recs)}"
#             assert len(set(recs)) == 10, "Recommendations should be unique"

#             assert session_store.redis.exists(session_store._get_sample_taken_key()), "Sample taken flag should have been set"

#             extra_songs = [generate_random_song_id() for _ in range(songs_per_user)]
#             session_store.set_random_recs(extra_songs)
#             new_total_recs = session_store.redis.llen(session_store._get_random_recs_key()) 
#             assert new_total_recs == 10, f"Expected 10 recommendations, shouldn't change after sample, but got {new_total_recs}"   

#             new_recs = session_store.get_random_recs()  
#             assert new_recs == recs, "Recommendations should be the same after sampling"

# def test_set_random_recs(session_store):
#     session_store.redis.flushdb()  
#     test_songs = [f"test_song_{i}" for i in range(5)]
#     session_store.set_random_recs(test_songs)
#     stored_songs = session_store.redis.lrange(session_store._get_random_recs_key(), 0, -1)
#     assert len(stored_songs) == 5, f"Expected 5 recommendations, but got {len(stored_songs)}"
#     assert all(song.decode() in test_songs for song in stored_songs), "Stored recommendations should match input"

# def test_get_random_recs_insufficient_data(session_store):
#     session_store.redis.flushdb()
#     test_songs = [generate_random_song_id() for i in range(50)]
#     session_store.set_random_recs(test_songs)
#     recs  = session_store.get_random_recs()
#     assert recs is None, f"Expected None, but got {recs}"



if __name__ == "__main__":
    pytest.main([__file__])
