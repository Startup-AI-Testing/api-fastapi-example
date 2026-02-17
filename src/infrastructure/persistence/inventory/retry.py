import time
import functools
from src.domain.inventory.errors.inventory_errors import ConcurrencyError

def retry_on_concurrency(max_retries: int = 3, delay: float = 0.1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ConcurrencyError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt)) # Exponential backoff
                        # Note: If using SQLAlchemy, we might need to rollback the session here
                        # but that depends on where the session is managed.
                        continue
                    raise last_exception
            return func(*args, **kwargs)
        return wrapper
    return decorator
