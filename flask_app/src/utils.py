import psutil
import logging
import functools
import contextlib
import time
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_memory_usage(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        before_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        logging.info(f"Memory usage before {func.__name__}: {before_memory:.2f} MB")
        
        result = func(*args, **kwargs)
        
        after_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        logging.info(f"Memory usage after {func.__name__}: {after_memory:.2f} MB")
        logging.info(f"Memory difference: {after_memory - before_memory:.2f} MB")
        
        return result
    return wrapper


def log_current_memory_usage():
    process = psutil.Process()
    memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    # logging.info(f"Current memory usage: {memory:.2f} MB")
    return memory


@contextlib.contextmanager
def track_memory_usage(operation):
    process = psutil.Process()
    before_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    start_time = time.time()
    yield
    after_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    end_time = time.time()
    memory_diff = after_memory - before_memory
    time_diff = end_time - start_time
    logging.info(f"{operation} memory usage: {memory_diff:.2f} MB in {time_diff:.2f} seconds")


def mem_usage(df):
    return f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"