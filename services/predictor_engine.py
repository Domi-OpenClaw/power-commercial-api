# -*- coding: utf-8 -*-
"""预测引擎"""
import datetime
import numpy as np
from typing import Dict, List, Tuple, Any
from models.config import PROVINCE_CONFIG, PROVINCE_LOAD
from services.weather import get_weather
from services.coal import get_coal_price
from services.predictor import storage_strategy, CHARGE_THRESHOLD, DISCHARGE_THRESHOLD

# 季节因子
SEASON_FACTOR = {
    1: 1.05, 2: 1.03, 3: 0.98, 4: 0.95, 5: 0.97, 6: 1.08,
    7: 1.12, 8: 1.10, 9: 1.02, 10: 0.97, 11: 1.00, 12: 1.08
}

# 典型日时段曲线
HOUR_CURVE = {
    0: 0.90, 1: 0.88, 2: 0.85, 3: 0.83, 4: 0.82, 5: 0.85,
    6: 0.92, 7: 1.05, 8: 1.12, 9: 1.08, 10: 0.95, 11: 0.80,
    12: 0.70, 13: 0.68, 14: 0.75, 15: 0.85, 16: 0.95, 17: 1.08,
    18: 1.15, 19: 1.18, 20: 1.10, 21: 1.00, 22: 0.92, 23: 0.88,
}

def get_load_now(province: str) -> float:
    base = PROVINCE_LOAD.get(province, 7000)
    h = datetime.datetime.now().hour
    if 9 <= h <= 11 or 18 <= h <= 21:
        return round(base * 1.12, 0)
    elif 23 <= h or h <= 6:
        return round(base * 0.85, 0)
    return round(base, 0)

def predict_24h(province: str, date_str: str = None) -> Dict[str, Any]:
    """
    生成24小时预测
    """
    cfg = PROVINCE_CONFIG[province]
    base_price = cfg["base_price"]
    coord = cfg["coord"]
    now = datetime.datetime.now()

    load = get_load_now(province)
    weather = get_weather(coord)
    coal = get_coal_price()
    month = now.month
    sf = SEASON_FACTOR.get(month, 1.0)

    hours_result = []
    charge_hours = []
    discharge_hours = []

    for h in range(24):
        curve = HOUR_CURVE.get(h, 1.0)
        solar = weather["solar_rad"]
        temp = weather["temp"]

        # 午间光伏压价（11-14时）
        if 11 <= h <= 14 and solar > 300:
            solar_discount = min(0.35, solar / 2000)
            curve *= (1 - solar_discount)

        # 温度修正
        if temp > 30:
            heat_adj = (temp - 30) * 0.02
        elif temp < 5:
            heat_adj = (5 - temp) * 0.015
        else:
            heat_adj = 0

        # 煤价传导
        coal_adj = (coal - 580) / 580 * 0.08

        # 负荷偏差
        base = PROVINCE_LOAD.get(province, 7000)
        load_adj = (load - base) / base * 0.15

        price = base_price * sf * curve * (1 + heat_adj + coal_adj + load_adj)
        std = price * 0.15
        p10 = round(max(-80, price - std), 2)
        p50 = round(price, 2)
        p90 = round(min(1300, price + std), 2)

        action, reason, signal = storage_strategy(p50)
        if signal == "charge":
            charge_hours.append(h)
        elif signal == "discharge":
            discharge_hours.append(h)

        hours_result.append({
            "hour": h,
            "p10_low": p10,
            "p50_median": p50,
            "p90_high": p90,
            "action": action,
            "action_reason": reason,
            "storage_signal": signal,
        })

    p50_values = [h["p50_median"] for h in hours_result]
    avg_p50 = round(np.mean(p50_values), 2)
    max_p50 = round(max(p50_values), 2)
    min_p50 = round(min(p50_values), 2)

    best_charge = min(charge_hours) if charge_hours else None
    best_discharge = max(discharge_hours) if discharge_hours else None

    return {
        "province": province,
        "date": date_str or now.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(timespec="seconds") + "+08:00",
        "market_type": cfg["market"],
        "data_reliability": {
            "star": cfg["star"],
            "score": cfg["reliability"],
            "warning": "⚠️模拟数据，非真实出清价",
        },
        "reference": {
            "coal_price_yuan_per_ton": coal,
            "load_mw": load,
            "weather": {
                "temp_celsius": weather["temp"],
                "wind_speed_ms": weather["wind_speed"],
                "solar_radiation": weather["solar_rad"],
            }
        },
        "forecast_24h": hours_result,
        "daily_summary": {
            "avg_p50": avg_p50,
            "max_p50": max_p50,
            "min_p50": min_p50,
            "charge_hours": charge_hours,
            "discharge_hours": discharge_hours,
            "best_charge_hour": best_charge,
            "best_discharge_hour": best_discharge,
        }
    }
