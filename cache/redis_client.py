import redis
import json
import hashlib
from typing import Any

redis_client = redis.Redis(host="localhost",port=6379,db=1,decode_responses=True)


class RedisCache:
    def __init__(self):
        self.client = redis_client

    def make_key(self, namespace: str, data: Any) -> str:
        json_data = json.dumps(data,sort_keys=True,ensure_ascii=False,default=str)
        hashed = hashlib.sha256(json_data.encode("utf-8")).hexdigest()
        return f"3ala_damanty:{namespace}:{hashed}"

    def get(self, key: str):
        value = self.client.get(key)
        if value is None: return None
        return json.loads(value)

    def set(self, key: str, value: Any, ttl=3600):
        json_data = json.dumps(value,ensure_ascii=False,default=str)
        self.client.setex(key, ttl, json_data)

    def delete(self, key: str):
        self.client.delete(key)