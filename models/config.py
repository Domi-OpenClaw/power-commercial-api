# -*- coding: utf-8 -*-
"""省份配置（从 MCP v3 同步）"""
from typing import Dict

PROVINCE_CONFIG: Dict[str, dict] = {
    "山东":     {"coord": (36.67, 117.0),  "star": "★★★★★", "reliability": 48, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 350},
    "广东":     {"coord": (23.13, 113.26), "star": "★★★★",  "reliability": 45, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 420},
    "山西":     {"coord": (37.87, 112.55), "star": "★★★★",  "reliability": 45, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 280},
    "浙江":     {"coord": (30.27, 120.15), "star": "★★★",   "reliability": 42, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 400},
    "湖北":     {"coord": (30.59, 114.31), "star": "★★★",   "reliability": 42, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 360},
    "甘肃":     {"coord": (36.06, 103.83), "star": "★★★",   "reliability": 42, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 250},
    "蒙西":     {"coord": (40.12, 107.10), "star": "★★",    "reliability": 40, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 320},
    "四川":     {"coord": (30.66, 104.04), "star": "★★",    "reliability": 40, "market": "正式现货",  "source": "合成模型+天气修正", "base_price": 300},
    "河北":     {"coord": (38.04, 114.48), "star": "★★",    "reliability": 41, "market": "试运行",    "source": "统计拟合", "base_price": 330},
    "江苏":     {"coord": (32.04, 118.76), "star": "★★",    "reliability": 42, "market": "试运行",    "source": "统计拟合", "base_price": 380},
    "安徽":     {"coord": (31.86, 117.28), "star": "★★",    "reliability": 41, "market": "试运行",    "source": "统计拟合", "base_price": 370},
    "福建":     {"coord": (26.08, 119.30), "star": "★★",    "reliability": 41, "market": "试运行",    "source": "统计拟合", "base_price": 360},
    "河南":     {"coord": (34.76, 113.65), "star": "★★",    "reliability": 42, "market": "试运行",    "source": "统计拟合", "base_price": 330},
    "湖南":     {"coord": (28.23, 112.93), "star": "★★",    "reliability": 41, "market": "试运行",    "source": "统计拟合", "base_price": 360},
    "重庆":     {"coord": (29.56, 106.55), "star": "★★",    "reliability": 41, "market": "试运行",    "source": "统计拟合", "base_price": 350},
    "陕西":     {"coord": (34.27, 108.94), "star": "★★",    "reliability": 41, "market": "试运行",    "source": "统计拟合", "base_price": 290},
    "辽宁":     {"coord": (41.80, 123.44), "star": "★★",    "reliability": 40, "market": "试运行",    "source": "统计拟合", "base_price": 300},
    "江西":     {"coord": (28.68, 115.86), "star": "★",     "reliability": 38, "market": "试运行",    "source": "统计拟合", "base_price": 340},
    "贵州":     {"coord": (26.65, 106.63), "star": "★",     "reliability": 38, "market": "试运行",    "source": "水电模型", "base_price": 300},
    "云南":     {"coord": (25.04, 102.71), "star": "★",     "reliability": 38, "market": "试运行",    "source": "水电模型", "base_price": 280},
    "吉林":     {"coord": (43.88, 125.33), "star": "★",     "reliability": 36, "market": "试运行",    "source": "统计拟合", "base_price": 310},
    "黑龙江":   {"coord": (45.80, 126.54), "star": "★",     "reliability": 36, "market": "试运行",    "source": "统计拟合", "base_price": 300},
    "内蒙古":   {"coord": (40.82, 111.75), "star": "★",     "reliability": 38, "market": "试运行",    "source": "统计拟合", "base_price": 260},
    "广西":     {"coord": (22.82, 108.31), "star": "★",     "reliability": 36, "market": "试运行",    "source": "统计拟合", "base_price": 350},
    "海南":     {"coord": (20.03, 110.32), "star": "☆",     "reliability": 33, "market": "试运行",    "source": "趋势预测", "base_price": 400},
    "宁夏":     {"coord": (38.47, 106.27), "star": "★",     "reliability": 35, "market": "试运行",    "source": "新能源拟合", "base_price": 240},
    "青海":     {"coord": (36.62, 101.78), "star": "★",     "reliability": 35, "market": "试运行",    "source": "新能源拟合", "base_price": 220},
    "西藏":     {"coord": (29.65, 91.17),  "star": "☆",     "reliability": 30, "market": "试运行",    "source": "极小电网参考", "base_price": 450},
}

PROVINCE_LOAD = {
    "山东": 8200, "广东": 11000, "山西": 3800, "浙江": 7200, "湖北": 4300, "甘肃": 2600, "蒙西": 4200, "四川": 4600,
    "河北": 5200, "江苏": 9000, "安徽": 3900, "福建": 3700, "河南": 5600, "湖南": 4100, "重庆": 2900, "陕西": 3000,
    "辽宁": 4400, "江西": 3400, "贵州": 3100, "云南": 3600, "吉林": 2200, "黑龙江": 2700, "内蒙古": 4200, "广西": 3800,
    "海南": 1100, "宁夏": 1200, "青海": 900, "西藏": 350,
}

PROVINCE_IDS = list(PROVINCE_CONFIG.keys())
