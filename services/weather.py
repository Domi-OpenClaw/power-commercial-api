# -*- coding: utf-8 -*-
"""
天气获取服务 - 零阻塞设计
策略：后台线程每30分钟刷新一次，API请求直接读内存缓存，无任何I/O等待
"""
import requests
import threading
import time
import numpy as np
from typing import Dict, Tuple

DEFAULT_WEATHER = {"temp": 25, "wind_speed": 4, "solar_rad": 500}
REQUEST_TIMEOUT = 4  # 秒
REFRESH_INTERVAL = 1800  # 30分钟刷新一次

# 内存缓存（进程内共享，线程安全）
_weather_cache: Dict[str, Dict[str, float]] = {}
_cache_lock = threading.RLock()
_refresh_thread: threading.Thread | None = None

def _coord_key(lat: float, lon: float) -> str:
    return f"{lat:.2f},{lon:.2f}"

def get_weather(coord: Tuple[float, float]) -> Dict[str, float]:
    """
    零阻塞：直接读内存缓存，无任何网络请求
    """
    lat, lon = coord
    key = _coord_key(lat, lon)
    with _cache_lock:
        if key in _weather_cache:
            return _weather_cache[key]
    return DEFAULT_WEATHER.copy()

def _fetch_weather_for_coord(coord: Tuple[float, float]) -> Dict[str, float]:
    lat, lon = coord
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,wind_speed_10m,direct_radiation",
                "forecast_days": 1,
                "timezone": "Asia/Shanghai"
            },
            timeout=REQUEST_TIMEOUT
        )
        d = r.json()
        hourly = d["hourly"]
        return {
            "temp": round(float(np.nanmean(hourly["temperature_2m"])), 1),
            "wind_speed": round(float(np.nanmean(hourly["wind_speed_10m"])), 1),
            "solar_rad": round(float(np.nanmean([x for x in hourly["direct_radiation"] if x is not None])), 1),
        }
    except Exception:
        return DEFAULT_WEATHER.copy()

def _refresh_all():
    """后台线程：批量刷新所有省份天气（启动时已同步刷新过，这里只做周期更新）"""
    while True:
        time.sleep(REFRESH_INTERVAL)
        try:
            _do_refresh()
        except Exception as e:
            print(f"[weather] 刷新失败: {e}")

def _do_refresh():
    """执行一次批量刷新"""
    from models.config import PROVINCE_CONFIG
    coords = set(cfg["coord"] for cfg in PROVINCE_CONFIG.values())
    for coord in coords:
        lat, lon = coord
        key = _coord_key(lat, lon)
        weather = _fetch_weather_for_coord(coord)
        with _cache_lock:
            _weather_cache[key] = weather
    print(f"[weather] 刷新完成，共 {len(coords)} 个地区")

def start_weather_refresh():
    """启动后台天气刷新线程（首次同步刷新，再启动后台）"""
    global _refresh_thread
    if _refresh_thread is None or not _refresh_thread.is_alive():
        # 首次同步刷新（阻塞最多30秒，之后的刷新在后台）
        print("[weather] 首次同步刷新...")
        _do_refresh()
        _refresh_thread = threading.Thread(target=_refresh_all, daemon=True, name="weather-refresh")
        _refresh_thread.start()
        print("[weather] 后台刷新线程已启动，每30分钟更新")
