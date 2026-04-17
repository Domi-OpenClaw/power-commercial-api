# ⚡ 电力现货价格预测 API

24h 滚动预测 28 个省的电力现货市场日前价格，支持储能充放电策略优化。

## 功能特性

- 🌍 **28 省覆盖**：正式现货市场 8 省 + 试运行 20 省
- ⏰ **24h 预测**：每整点前推未来 24h 分时价格（P10/P50/P90 分位）
- 🔋 **储能策略**：自动输出充电时段（低价）与放电时段（高价）
- 🌤️ **天气集成**：实时天气数据影响新能源出力预测
- 📊 **历史参考**：近 7 日价格分布统计

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml，填入你的 API Key
```

### 3. 启动服务

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 10129
```

### 4. 测试

```bash
# 健康检查
curl http://localhost:10129/health

# 省份列表
curl -H "api-key: YOUR_API_KEY" http://localhost:10129/api/v1/provinces

# 预测（山东 2026-04-18）
curl -H "api-key: YOUR_API_KEY" \
  "http://localhost:10129/api/v1/forecasts?province=山东&date=2026-04-18"
```

### 5. Python 调用示例

```python
import requests

resp = requests.get(
    "http://localhost:10129/api/v1/forecasts",
    params={"province": "山东", "date": "2026-04-18"},
    headers={"api-key": "YOUR_API_KEY"},
    timeout=30
)
data = resp.json()["data"]
print(f"山东预测均价: {data['daily_summary']['avg_p50']} 元/MWh")
print(f"充电时段: {data['daily_summary']['charge_hours']}")
print(f"放电时段: {data['daily_summary']['discharge_hours'] or '无'}")
```

## API 文档

启动后访问：`http://localhost:10129/docs`（FastAPI 自动生成 Swagger 文档）

## 支持的省份

| 正式现货市场 | 试运行省份 |
|------------|-----------|
| 山东、山西、广东、浙江、四川、湖北、甘肃、蒙西 | 云南、内蒙古、吉林、宁夏、安徽、广西、江苏、江西、河北、河南、海南、湖南、福建、西藏、贵州、辽宁、重庆、陕西、青海、黑龙江 |

## 部署方式

### systemd 守护进程

```bash
sudo cp power-api.service /etc/systemd/system/
sudo systemctl enable power-api
sudo systemctl start power-api
```

### Docker（可选）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10129"]
```

## 数据说明

**价格单位**：元/MWh（= 元/兆瓦时）

**分位含义**：
- P10（低价区间）：充电最佳时机
- P50（中位预测）：基准预期
- P90（高价区间）：放电参考

**储能策略建议**：
- `charge_hours`：P10 低价时段，适合储能充电
- `discharge_hours`：P90 高价时段，适合储能放电

## 免责声明

本 API 预测结果仅供参考，不构成投资建议。实际电力交易请遵循各地电网公司和电力交易中心的相关规定。

## License

MIT
