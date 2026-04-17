# -*- coding: utf-8 -*-
"""储能策略服务"""
from datetime import datetime

# 阈值参考：山东2026年现货价格区间
CHARGE_THRESHOLD = 280  # 低于此价充电
DISCHARGE_THRESHOLD = 420  # 高于此价放电

def storage_strategy(p50: float) -> tuple:
    """返回 (action, reason, signal)"""
    if p50 < CHARGE_THRESHOLD:
        return "充电", "谷价充电，储能套利窗口", "charge"
    elif p50 > DISCHARGE_THRESHOLD:
        return "放电", "峰价放电，实现高收益", "discharge"
    else:
        return "观望", "平价待机，等待最佳价差", "hold"
