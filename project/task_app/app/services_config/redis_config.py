import redis
import json
from task_app.app.services_config.rbac_keycloack import require_role
from fastapi import HTTPException, status, Depends


redis_client = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

def get_cache(key: str):
    """Fetch value from Redis cache"""
    value = redis_client.get(key)
    return json.loads(value) if value else None

def set_cache(key: str, value, ttl: int = 60):
    """Set cache with a TTL (in seconds)"""
    redis_client.set(key, json.dumps(value), ex=ttl)

def invalidate_cache(key_pattern: str):
    """Delete keys matching a pattern"""
    for key in redis_client.scan_iter(key_pattern):
        redis_client.delete(key)



RATE_LIMIT = 100
WINDOW = 60  # seconds

def rate_limiter(user=Depends(require_role("admin", "user"))):
    key = f"rate_limit:{user.username}"

    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, WINDOW)

    if current > RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
