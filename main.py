# -*- coding: utf-8 -*-
"""
电力现货价格预测商用 API — FastAPI 入口
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from config_loader import get

from routers import forecast, admin
from services.cache import get_redis
from services.weather import start_weather_refresh
from services.coal import start_coal_refresh

# ========== FastAPI 配置 ==========
app = FastAPI(
    title="电力现货价格预测 API",
    description="""
## ⚠️ 重要声明

本 API 数据为**模拟测试用途**，非真实市场出清价格。

**不可直接用于**：
- ❌ 电力交易商用决策
- ❌ 储能系统自动化控制
- ❌ 任何涉及真金白银的交易

**适用场景**：
- ✅ 内部模拟回测
- ✅ 储能策略研究
- ✅ 价格趋势分析参考
    """,
    version="0.1.0",
    docs_url="/docs" if os.getenv("DOCS_ENABLED", "true").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DOCS_ENABLED", "true").lower() == "true" else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(forecast.router)
app.include_router(admin.router)

# ========== Dashboard 静态文件路由 ==========
DASHBOARD_DIR = Path(__file__).parent / "dashboard"

@app.get("/dashboard")
def serve_dashboard():
    """仪表盘首页"""
    index_file = DASHBOARD_DIR / "index.html"
    if index_file.exists():
        return RedirectResponse(url="/dashboard/")
    return RedirectResponse(url="/dashboard/index.html")

@app.get("/dashboard/{path:path}")
def serve_dashboard_files(path: str):
    """仪表盘静态资源"""
    file_path = DASHBOARD_DIR / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    # fallback to index
    index_file = DASHBOARD_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(status_code=404, content={"error": "Dashboard not found"})

# ========== 健康检查 ==========
@app.get("/health")
def health_check():
    redis_ok = False
    try:
        r = get_redis()
        if r:
            r.ping()
            redis_ok = True
    except:
        pass

    return {
        "status": "ok",
        "version": "0.1.0",
        "redis": "connected" if redis_ok else "not connected (using local cache)",
    }

# ========== 全局错误处理 ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": f"服务器内部错误：{str(exc)}",
            "request_id": None,
        }
    )

# ========== 定时任务（可选）==========
def daily_task():
    """每日0点执行：清理过期缓存等"""
    import logging
    logging.info("每日定时任务执行")

if os.getenv("SCHEDULER_ENABLED", "false").lower() == "true":
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_task, "cron", hour=0, minute=30)
    scheduler.start()

# ========== 启动时初始化 ==========
start_weather_refresh()
start_coal_refresh()

# ========== 启动 ==========
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVER_PORT", get("server.port", 10129)))
    uvicorn.run(app, host="0.0.0.0", port=port)

# ========== 知识图谱静态文件 ==========
kg_path = Path(__file__).parent / "static" / "kg"
if kg_path.exists():
    app.mount("/kg", StaticFiles(directory=str(kg_path), html=True), name="kg")
