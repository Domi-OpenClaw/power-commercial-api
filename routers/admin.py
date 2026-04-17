# -*- coding: utf-8 -*-
"""管理接口路由"""
from fastapi import APIRouter, HTTPException, Header
from models.schemas import APIResponse, PriceDataRequest, PriceDataResponse
from models.config import PROVINCE_CONFIG
from services.cache import cache_real_data, new_request_id
from config_loader import get

router = APIRouter(prefix="/api/v1/admin", tags=["管理"])

def _check_admin(api_key: str = Header(...)) -> str:
    valid_key = get("security.admin_key", "sk-admin-power-2026")
    if api_key != valid_key:
        raise HTTPException(status_code=403, detail="Admin API Key 无效")
    return api_key

@router.post("/price-data", response_model=APIResponse)
def inject_price_data(
    body: PriceDataRequest,
    api_key: str = Header(...),
):
    """
    手动灌入真实价格数据，用于提升预测精度

    示例请求：
    ```json
    {
      "province": "山东",
      "date": "2026-04-16",
      "prices": [
        {"hour": 0, "day_ahead": 320.5, "real_time": 315.2},
        {"hour": 1, "day_ahead": 318.0, "real_time": 312.0}
      ]
    }
    ```
    """
    req_id = new_request_id()

    try:
        _check_admin(api_key)
    except HTTPException as e:
        return APIResponse(code=e.status_code, msg=e.detail, request_id=req_id)

    if body.province not in PROVINCE_CONFIG:
        return APIResponse(code=404, msg=f"不支持的省份：{body.province}", request_id=req_id)

    if len(body.prices) == 0:
        return APIResponse(code=400, msg="prices 不能为空", request_id=req_id)

    prices = [
        {"hour": p.hour, "day_ahead": p.day_ahead, "real_time": p.real_time}
        for p in body.prices
    ]

    cached = cache_real_data(body.province, body.date, prices, source="manual_inject")

    return APIResponse(code=200, msg="success", data={
        "status": "ok",
        "province": body.province,
        "date": body.date,
        "cached": cached,
    }, request_id=req_id)
