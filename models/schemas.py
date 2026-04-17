# -*- coding: utf-8 -*-
"""Pydantic 模型 / API 请求响应格式"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# ========== 通用 ==========
class APIResponse(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Optional[dict] = None
    request_id: Optional[str] = None

class ErrorResponse(BaseModel):
    code: int
    msg: str
    request_id: Optional[str] = None

# ========== 数据可靠度 ==========
class DataReliability(BaseModel):
    star: str
    score: int
    warning: str = "⚠️模拟数据，非真实出清价"

# ========== 参考数据 ==========
class WeatherRef(BaseModel):
    temp_celsius: float
    wind_speed_ms: float
    solar_radiation: float

class Reference(BaseModel):
    coal_price_yuan_per_ton: float
    load_mw: float
    weather: WeatherRef

# ========== 每小时预测 ==========
class HourForecast(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    p10_low: float = Field(..., description="低价风险分位数")
    p50_median: float = Field(..., description="预测中枢分位数")
    p90_high: float = Field(..., description="尖峰风险分位数")
    action: Literal["充电", "放电", "观望"]
    action_reason: str
    storage_signal: Literal["charge", "discharge", "hold"]

# ========== 日汇总 ==========
class DailySummary(BaseModel):
    avg_p50: float
    max_p50: float
    min_p50: float
    charge_hours: List[int]
    discharge_hours: List[int]
    best_charge_hour: int
    best_discharge_hour: Optional[int] = None

# ========== 预测主体 ==========
class ForecastData(BaseModel):
    province: str
    date: str
    generated_at: str
    market_type: str
    data_reliability: DataReliability
    reference: Reference
    forecast_24h: List[HourForecast]
    daily_summary: DailySummary
    important_notice: str = "⚠️ 本API数据为模拟测试用途，非真实市场出清价格，不可直接用于电力交易商用决策。"

# ========== 省份 ==========
class ProvinceInfo(BaseModel):
    province: str
    market: str
    star: str
    reliability: int
    source: str

class ProvinceListResponse(BaseModel):
    formal_market: List[str]
    pilot_market: List[str]
    total: int

# ========== 手动灌数据 ==========
class PriceEntry(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    day_ahead: Optional[float] = None
    real_time: Optional[float] = None

class PriceDataRequest(BaseModel):
    province: str
    date: str
    prices: List[PriceEntry]

class PriceDataResponse(BaseModel):
    status: str
    province: str
    date: str
    cached: int
