# -*- coding: utf-8 -*-
"""煤价获取服务"""
import requests
import os

DEFAULT_COAL_PRICE = 580.0  # 4月环渤海参考价约770，偏低留安全边际

def get_coal_price() -> float:
    """
    尝试获取真实煤价信号，失败时返回默认值
    """
    # 1. 尝试国煤中心
    try:
        r = requests.get(
            "https://www.cctd.com/api/index?type=2",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            },
            timeout=8
        )
        if r.status_code == 200:
            d = r.json()
            price = d.get("data", [{}])[0].get("price", None)
            if price and 400 < float(price) < 1200:
                return round(float(price), 2)
    except Exception:
        pass

    # 2. 备用：Sina期货（秦皇岛动力煤主力）
    try:
        r2 = requests.get(
            "https://hq.sinajs.cn/list=hf_CZC",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.sina.com.cn"
            },
            timeout=8
        )
        if r2.status_code == 200:
            text = r2.text
            nums = [x.strip() for x in text.split(",") if x.strip().replace(".", "").replace("-", "").isdigit()]
            if nums:
                return round(float(nums[0]) * 0.98, 2)  # 吨换算
    except Exception:
        pass

    return DEFAULT_COAL_PRICE
