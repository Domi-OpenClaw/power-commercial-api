#!/bin/bash
# 电力现货价格预测 API 启动脚本
# 用法: ./start.sh
# 或直接: systemctl start power-api

WORKDIR="/home/admin/.openclaw/workspace/servers/power-commercial-api"
LOG="/var/log/power-api.log"
PIDFILE="/tmp/power-api.pid"

# 检查是否已在运行
if ss -tlnp 2>/dev/null | grep -q 10129; then
    echo "⚠️  服务已在运行 (端口 10129)，请先停止: fuser -k 10129/tcp"
    exit 1
fi

cd "$WORKDIR"
nohup python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 10129 \
    --log-level warning \
    >> "$LOG" 2>&1 &

echo $! > "$PIDFILE"
echo "✅ 服务已启动 PID=$(cat $PIDFILE) on :10129"
echo "   日志: $LOG"
echo "   测试: curl -H 'api-key: sk-test-power-2026' http://localhost:10129/api/v1/provinces"
