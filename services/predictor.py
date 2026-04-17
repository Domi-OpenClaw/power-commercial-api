# -*- coding: utf-8 -*-
"""储能策略服务"""
from datetime import datetime

# 阈值参考：全国各省2026年现货价格区间（基于历史数据动态调整）
# 充电阈值：低于此价入库存储（通常为光伏富余时段的低谷价）
# 放电阈值：高于此价释放储能（通常为晚高峰需求紧张时段）
CHARGE_THRESHOLD = 300  # 低于300元/MWh时充电（光伏富余/夜间低谷）
DISCHARGE_THRESHOLD = 400  # 高于400元/MWh时放电（晚高峰需求紧张）

def storage_strategy(p50: float) -> tuple:
    """返回 (action, reason, signal)"""
    if p50 < CHARGE_THRESHOLD:
        return "充电", "谷价充电，储能套利窗口", "charge"
    elif p50 > DISCHARGE_THRESHOLD:
        return "放电", "峰价放电，实现高收益", "discharge"
    else:
        return "观望", "平价待机，等待最佳价差", "hold"
