# -*- coding: utf-8 -*-
"""缓存服务"""
import json
import os
import datetime
import uuid

DATA_DIR = os.path.dirname(os.path.abspath(__file__)).replace("/services", "/data")
CACHE_FILE = os.path.join(DATA_DIR, "price_cache.json")

def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def _save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cache_real_data(province: str, date: str, prices: list, source: str = "manual"):
    """缓存真实价格数据"""
    cache = _load_cache()
    key = f"{province}_{date}"
    cache[key] = {
        "prices": prices,
        "source": source,
        "updated": datetime.datetime.now().isoformat()
    }
    _save_cache(cache)
    return len(prices)

def get_cached_prices(province: str, days_back: int = 7):
    """获取缓存中最近的有效数据"""
    cache = _load_cache()
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    best = []
    for key, entry in cache.items():
        if key.startswith(f"{province}_"):
            try:
                updated_date = entry["updated"][:10]
                if updated_date >= cutoff and entry.get("prices"):
                    best.append((key, entry))
            except:
                pass
    if not best:
        return None
    best.sort(key=lambda x: x[1].get("updated", ""), reverse=True)
    return best[0][1]["prices"]

def new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"

# Redis缓存（可选，未连接时优雅降级）
_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db = int(os.getenv("REDIS_DB", 0))
        _redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True, socket_connect_timeout=2)
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None

def cache_get(key: str):
    r = get_redis()
    if r:
        try:
            val = r.get(key)
            return val
        except:
            pass
    return None

def cache_set(key: str, value: str, ttl: int = 3600):
    r = get_redis()
    if r:
        try:
            r.setex(key, ttl, value)
            return True
        except Exception:
            return False
    return False
