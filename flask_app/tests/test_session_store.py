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

# Fixture for SessionStore


def generate_random_song_id():
    """Generate a random song ID prefixed with the user ID for easy identification."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=22))

    # return random.choice(pandas.read_csv('session_store_random.csv')['track_id'])

def test_multi_user_random_recs(session_store):
    # Clear any existing data
    session_store.redis.flushdb()

    num_users = 20
    songs_per_user = 15
    
    for user in range(num_users):
        user_songs = [generate_random_song_id() for _ in range(songs_per_user)]
        session_store.set_random_recs(user_songs)

        # Check total recommendations
        total_recs = session_store.redis.llen(session_store._get_random_recs_key())

        if user < 13:
            assert total_recs == (user+1) * songs_per_user, f"Expected {(user+1) * songs_per_user} recommendations, but got {total_recs}"
        else:
            # Test initial sampling
            recs = session_store.get_random_recs()
            assert recs is not None, "Expected recommendations, but got None"
            assert len(recs) == 10, f"Expected 10 recommendations, but got {len(recs)}"
            assert len(set(recs)) == 10, "Recommendations should be unique"

            assert session_store.redis.exists(session_store._get_sample_taken_key()), "Sample taken flag should have been set"

            extra_songs = [generate_random_song_id() for _ in range(songs_per_user)]
            session_store.set_random_recs(extra_songs)
            new_total_recs = session_store.redis.llen(session_store._get_random_recs_key()) 
            assert new_total_recs == 10, f"Expected 10 recommendations, shouldn't change after sample, but got {new_total_recs}"   

            new_recs = session_store.get_random_recs()  
            assert new_recs == recs, "Recommendations should be the same after sampling"

def test_set_random_recs(session_store):
    session_store.redis.flushdb()  
    test_songs = [f"test_song_{i}" for i in range(5)]
    session_store.set_random_recs(test_songs)
    stored_songs = session_store.redis.lrange(session_store._get_random_recs_key(), 0, -1)
    assert len(stored_songs) == 5, f"Expected 5 recommendations, but got {len(stored_songs)}"
    assert all(song.decode() in test_songs for song in stored_songs), "Stored recommendations should match input"

def test_get_random_recs_insufficient_data(session_store):
    session_store.redis.flushdb()
    test_songs = [generate_random_song_id() for i in range(50)]
    session_store.set_random_recs(test_songs)
    recs  = session_store.get_random_recs()
    assert recs is None, f"Expected None, but got {recs}"

# Optional: Add a fixture to clear Redis before/after tests if needed
@pytest.fixture(autouse=True)
def clear_redis(session_store):
    yield
    session_store.redis.flushdb()  # Clear Redis after each test

if __name__ == "__main__":
    pytest.main([__file__])
