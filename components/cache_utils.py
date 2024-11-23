import functools
import json
import os
import pickle
from typing import Callable, Any
from datetime import datetime, timedelta

def flexible_cache(backend: str = 'memory', maxsize: int = 128, ttl: int = 3600):
    """
    A flexible caching decorator that supports different backend storage options.
    
    :param backend: The caching backend to use ('memory', 'disk', or 'database')
    :param maxsize: Maximum size of the cache (for memory backend)
    :param ttl: Time to live for cache entries in seconds (default 1 hour)
    """
    def decorator(func: Callable) -> Callable:
        if backend == 'memory':
            @functools.lru_cache(maxsize=maxsize)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        
        elif backend == 'disk':
            cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            def wrapper(*args, **kwargs):
                cache_key = json.dumps((func.__name__, args, kwargs), sort_keys=True)
                cache_file = os.path.join(cache_dir, f"{hash(cache_key)}.pkl")
                
                if os.path.exists(cache_file):
                    with open(cache_file, 'rb') as f:
                        timestamp, result = pickle.load(f)
                    if datetime.now() - timestamp < timedelta(seconds=ttl):
                        return result
                
                result = func(*args, **kwargs)
                with open(cache_file, 'wb') as f:
                    pickle.dump((datetime.now(), result), f)
                return result
            return wrapper
        
        elif backend == 'database':
            # Implement database caching logic here
            # This is a placeholder and should be implemented based on your database setup
            def wrapper(*args, **kwargs):
                # Placeholder for database caching logic
                return func(*args, **kwargs)
            return wrapper
        
        else:
            raise ValueError(f"Unsupported cache backend: {backend}")
    
    return decorator

def clear_cache(backend: str = 'all'):
    """
    Clear the cache for the specified backend.
    
    :param backend: The backend to clear ('memory', 'disk', 'database', or 'all')
    """
    if backend in ['memory', 'all']:
        # Clear memory cache
        # Note: This will only clear caches created in the current Python session
        for name, item in globals().items():
            if callable(item) and hasattr(item, 'cache_clear'):
                item.cache_clear()
    
    if backend in ['disk', 'all']:
        # Clear disk cache
        cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                os.remove(os.path.join(cache_dir, file))
    
    if backend in ['database', 'all']:
        # Clear database cache
        # Implement database cache clearing logic here
        pass

# Example usage:
# @flexible_cache(backend='disk', ttl=3600)
# def expensive_function(arg1, arg2):
#     # Expensive computation here
#     return result