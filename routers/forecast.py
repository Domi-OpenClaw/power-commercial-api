# -*- coding: utf-8 -*-
"""预测接口路由"""
from fastapi import APIRouter, Query, HTTPException, Header
from typing import Optional
from datetime import datetime
import json

from models.schemas import APIResponse, HourForecast, DailySummary, DataReliability, Reference, WeatherRef
from models.config import PROVINCE_CONFIG, PROVINCE_IDS
from services.predictor_engine import predict_24h
from services.cache import cache_get, cache_set, new_request_id
from config_loader import get

router = APIRouter(prefix="/api/v1", tags=["预测"])

def _check_api_key(api_key: str = Header(...)) -> str:
    """验证API Key"""
    valid_key = get("security.api_key", "sk-test-power-2026")
    if api_key != valid_key:
        raise HTTPException(status_code=403, detail="API Key 无效")
    return api_key

@router.get("/forecasts", response_model=APIResponse)
def get_forecast(
    province: str = Query(..., description="省份名称，如：山东"),
    date: str = Query(..., description="日期，格式：YYYY-MM-DD"),
    api_key: str = Header(...),
    request_id: Optional[str] = None,
):
    """
    获取指定省份和日期的24小时电力现货价格预测
    """
    req_id = request_id or new_request_id()

    # 1. 校验API Key
    try:
        _check_api_key(api_key)
    except HTTPException as e:
        return APIResponse(code=e.status_code, msg=e.detail, request_id=req_id)

    # 2. 校验省份
    if province not in PROVINCE_CONFIG:
        return APIResponse(
            code=404,
            msg=f"不支持的省份：{province}，支持列表见 /api/v1/provinces",
            request_id=req_id
        )

    # 3. 校验日期
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return APIResponse(
            code=400,
            msg="日期格式错误，需为 YYYY-MM-DD，如：2026-04-18",
            request_id=req_id
        )

    # 4. 检查缓存
    cache_key = f"fc:{province}:{date}"
    cached = cache_get(cache_key)
    if cached:
        return APIResponse(code=200, msg="success (cached)", data=json.loads(cached), request_id=req_id)

    # 5. 生成预测
    result = predict_24h(province, date)
    result["generated_at"] = datetime.now().isoformat(timespec="seconds") + "+08:00"

    # 6. 缓存结果（1小时）
    cache_set(cache_key, json.dumps(result, ensure_ascii=False), ttl=3600)

    return APIResponse(code=200, msg="success", data=result, request_id=req_id)

@router.get("/provinces", response_model=APIResponse)
def list_provinces(api_key: str = Header(...)):
    """查询支持的省份列表"""
    try:
        _check_api_key(api_key)
    except HTTPException as e:
        return APIResponse(code=e.status_code, msg=e.detail)

    formal = sorted([p for p, c in PROVINCE_CONFIG.items() if c["market"] == "正式现货"])
    pilot = sorted([p for p, c in PROVINCE_CONFIG.items() if c["market"] == "试运行"])

    return APIResponse(code=200, msg="success", data={
        "formal_market": formal,
        "formal_count": len(formal),
        "pilot_market": pilot,
        "pilot_count": len(pilot),
        "total": len(PROVINCE_CONFIG)
    })

@router.get("/provinces/{province}", response_model=APIResponse)
def get_province(province: str, api_key: str = Header(...)):
    """查询单个省份详情"""
    try:
        _check_api_key(api_key)
    except HTTPException as e:
        return APIResponse(code=e.status_code, msg=e.detail)

    if province not in PROVINCE_CONFIG:
        return APIResponse(code=404, msg=f"不支持的省份：{province}")

    cfg = PROVINCE_CONFIG[province]
    return APIResponse(code=200, msg="success", data={
        "province": province,
        "market": cfg["market"],
        "star": cfg["star"],
        "reliability": cfg["reliability"],
        "source": cfg["source"],
        "base_price": cfg["base_price"],
    })
