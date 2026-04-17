# 电力现货价格预测商用 API — 规划文档
> 版本：v0.1 | 日期：2026-04-17 | 状态：规划中

---

## 1. 核心定位

**面向场景**：储能运营商充放电策略参考、内部模拟回测

**NOT 商用决策**：本 API 明确标注为模拟测试数据，不可直接用于电力交易

**目标用户**：内部团队 / 合作储能运营商

---

## 2. 技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| 框架 | FastAPI | 高并发、自动化文档 |
| 缓存 | Redis | 生产环境已配置 |
| 存储 | JSON文件（`/data/`） | 轻量、无外部依赖 |
| 模型 | 本地LightGBM（可选） | 可升级 |
| 部署 | uvicorn | 异步高性能 |
| 容器 | Docker | 便于分发 |

---

## 3. API 设计原则

### 3.1 RESTful 规范
- 资源命名：名词复数 `/forecasts`
- HTTP 方法：GET 查询，POST 写入
- 状态码：200/400/401/403/404/429/500

### 3.2 版本管理
- 路径版本：`/api/v1/`
- 内部版本：`X-API-Version: 2026-04-17`
- 升级策略：v1 稳定后出 v2，v1 至少维护 6 个月

### 3.3 认证
- API Key 认证：`X-API-Key` header
- 存储：`config.yaml`（不硬编码在代码）
- 限流：100次/分钟（参考生产代码）

---

## 4. 数据模型

### 4.1 省份配置（已确定）
```
PROVINCE_CONFIG: {
  province_id: "山东",
  market_type: "正式现货" | "试运行",
  star_level: "★★★★★",
  reliability: 48,    // 已砍半
  base_price: 350,   // 元/MWh
  coord: (36.67, 117.0),
  source: "合成模型+天气修正",
}
```

### 4.2 预测响应（ForecastResponse）
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "province": "山东",
    "date": "2026-04-18",
    "generated_at": "2026-04-17T09:39:00+08:00",
    "market_type": "正式现货",
    "data_reliability": {
      "star": "★★★★★",
      "score": 48,
      "warning": "⚠️模拟数据，非真实出清价"
    },
    "reference": {
      "coal_price_yuan_per_ton": 580,
      "load_mw": 9184,
      "weather": {
        "temp_celsius": 21.5,
        "wind_speed_ms": 7.9,
        "solar_radiation": 222.2
      }
    },
    "forecast_24h": [
      {
        "hour": 0,
        "p10_low": 258.94,
        "p50_median": 304.64,
        "p90_high": 350.33,
        "action": "观望",
        "action_reason": "平价待机，等待最佳价差",
        "storage_signal": "hold"
      }
    ],
    "daily_summary": {
      "avg_p50": 312.45,
      "max_p50": 399.41,
      "min_p50": 230.17,
      "charge_hours": [4, 11, 12, 13, 14],
      "discharge_hours": [],
      "best_charge_hour": 13,
      "best_discharge_hour": 19
    }
  }
}
```

### 4.3 错误响应（ErrorResponse）
```json
{
  "code": 400,
  "msg": "参数错误：日期格式需为 YYYY-MM-DD",
  "request_id": "req_abc123"
}
```

---

## 5. 接口设计

### 5.1 预测接口
```
GET /api/v1/forecasts
Query Params:
  - province: str (required)  省名
  - date: str (required)      YYYY-MM-DD
  - quantiles: str (optional) "p10,p50,p90" 默认全部
Response: ForecastResponse
```

### 5.2 省份列表
```
GET /api/v1/provinces
Response: {
  "formal_market": ["山东", "广东", ...],
  "pilot_market": ["河北", "江苏", ...],
  "total": 28
}
```

### 5.3 单省详情
```
GET /api/v1/provinces/{province}
Response: ProvinceDetail
```

### 5.4 手动灌入真实数据
```
POST /api/v1/admin/price-data
Body: {
  "province": "山东",
  "date": "2026-04-16",
  "prices": [{"hour": 0, "day_ahead": 320.5, "real_time": 315.2}, ...]
}
Response: {"status": "ok", "cached": 24}
```

### 5.5 健康检查
```
GET /health
Response: {"status": "ok", "version": "0.1.0", "redis": "connected"}
```

---

## 6. 缓存策略

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 预测结果 | 1小时 | 同一省+日期不重复计算 |
| 省份配置 | 24小时 | 基本不变 |
| 天气数据 | 30分钟 | Open-Meteo 缓存 |
| 煤价数据 | 6小时 | 国煤中心日指数 |

---

## 7. 目录结构

```
power-commercial-api/
├── main.py              # FastAPI 入口
├── config.py            # 配置（API keys, Redis, 限流）
├── routers/
│   ├── forecast.py      # 预测相关接口
│   ├── province.py      # 省份查询接口
│   └── admin.py         # 管理接口（灌数据）
├── services/
│   ├── predictor.py     # 预测引擎
│   ├── cache.py         # Redis 缓存
│   ├── coal.py          # 煤价获取
│   ├── weather.py        # 天气获取
│   └── storage.py       # 储能策略
├── models/
│   ├── schemas.py       # Pydantic 模型
│   └── config.py        # 省份配置
├── data/
│   └── price_cache.json # 本地价格缓存
├── tests/
│   ├── test_forecast.py
│   └── test_storage.py
├── Dockerfile
├── docker-compose.yml   # Redis + API
└── requirements.txt
```

---

## 8. 部署方案

### 8.1 Docker Compose（开发/测试）
```yaml
services:
  api:
    build: .
    ports: ["10129:10129]
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
```

### 8.2 生产环境
- 独立服务器 or 云容器
- Nginx 反向代理
- HTTPS 强制
- systemd 管理进程

---

## 9. 规划里程碑

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| P0 | FastAPI 骨架 + 预测接口 | 本次 |
| P0 | 省份配置 + 错误处理 | 本次 |
| P1 | Redis 缓存集成 | P0后 |
| P1 | 限流 + 认证 | P0后 |
| P2 | 手动灌数据接口 | P0后 |
| P2 | 每日定时任务（模型更新） | P1后 |
| P3 | 历史回测接口 | 后续 |

---

## 10. 待确认

1. **是否需要 Docker 部署**？还是直接在服务器上跑 uvicorn？
2. **API Key 如何管理**？固定 key 还是动态发放？
3. **是否需要 API 文档页面**？FastAPI 自动生成可关闭
4. **返回格式**：`{"code": 200, "data": ...}`（统一）还是直接返回数据（RESTful）？
