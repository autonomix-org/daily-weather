import time, functools
from utils.logger import get_logger

logger = get_logger(__name__)

def retry(times=3, delay=2, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    logger.warning("Attempt %d/%d failed: %s", attempt, times, e)
                    if attempt < times:
                        time.sleep(delay)
            raise RuntimeError(f"{fn.__name__} failed after {times} attempts")
        return wrapper
    return decorator
