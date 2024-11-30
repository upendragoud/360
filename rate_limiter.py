# rate_limiter.py

from flask import request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

# A dictionary to store the request counts
request_counts = defaultdict(int)

# A dictionary to store the time when the user can make requests again
blocked_until = defaultdict(lambda: datetime(1900, 1, 1))

def rate_limiter(limit, period_in_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            remote_address = request.remote_addr

            if blocked_until[remote_address] > datetime.now():
                return jsonify({"msg": "Too many requests, try again later."}), 429

            if request_counts[remote_address] >= limit:
                blocked_until[remote_address] = datetime.now() + timedelta(seconds=period_in_seconds)
                request_counts[remote_address] = 0
                return jsonify({"msg": "Too many requests, try again later."}), 429

            request_counts[remote_address] += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator
