#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API 快速测试脚本"""
import sys
sys.path.insert(0, '/home/admin/.openclaw/workspace/servers/power-commercial-api')

import time
import uvicorn
from main import app

def run_tests():
    # 启动服务器（daemon线程）
    config = uvicorn.Config(app, host='127.0.0.1', port=10129, log_level='error', access_log=False)
    server = uvicorn.Server(config)
    import threading
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    time.sleep(20)  # 等待启动时天气同步刷新完成

    import requests

    print("=== Test 1: 健康检查 ===")
    r = requests.get('http://127.0.0.1:10129/health', timeout=5)
    print(r.json())
    assert r.json()['status'] == 'ok', "health failed"

    print("\n=== Test 2: 省份列表 ===")
    r = requests.get('http://127.0.0.1:10129/api/v1/provinces',
                     headers={'api-key': 'sk-test-power-2026'}, timeout=5)
    j = r.json()
    print(f"正式现货: {j['data']['formal_count']}省 | 试运行: {j['data']['pilot_count']}省 | 总计: {j['data']['total']}")
    assert j['code'] == 200

    print("\n=== Test 3: 省份详情 ===")
    r = requests.get('http://127.0.0.1:10129/api/v1/provinces/山东',
                     headers={'api-key': 'sk-test-power-2026'}, timeout=5)
    j = r.json()['data']
    print(f"{j['province']} {j['star']} 可靠度{j['reliability']} | {j['market']}")

    print("\n=== Test 4: 山东预测 ===")
    r = requests.get('http://127.0.0.1:10129/api/v1/forecasts',
                     params={'province': '山东', 'date': '2026-04-18'},
                     headers={'api-key': 'sk-test-power-2026'}, timeout=20)
    j = r.json()
    assert j['code'] == 200, f"failed: {j}"
    d = j['data']
    ds = d['daily_summary']
    print(f"省份: {d['province']} | 市场: {d['market_type']}")
    print(f"avg_p50: {ds['avg_p50']} | max: {ds['max_p50']} | min: {ds['min_p50']}")
    print(f"充电时段: {ds['charge_hours']} → 最佳: {ds['best_charge_hour']}时")
    print(f"放电时段: {ds['discharge_hours'] or '无'}")
    print(f"可靠度: {d['data_reliability']['star']} {d['data_reliability']['score']}")

    print("\n=== Test 5: 广东预测 ===")
    r = requests.get('http://127.0.0.1:10129/api/v1/forecasts',
                     params={'province': '广东', 'date': '2026-04-18'},
                     headers={'api-key': 'sk-test-power-2026'}, timeout=20)
    j = r.json()
    ds = j['data']['daily_summary']
    print(f"省份: {j['data']['province']} | avg: {ds['avg_p50']} | charge: {ds['charge_hours']} | discharge: {ds['discharge_hours'] or '无'}")

    print("\n=== Test 6: 错误处理（无效省份）===")
    r = requests.get('http://127.0.0.1:10129/api/v1/forecasts',
                     params={'province': '不存在省', 'date': '2026-04-18'},
                     headers={'api-key': 'sk-test-power-2026'}, timeout=5)
    j = r.json()
    print(f"无效省份 code: {j['code']} | msg: {j['msg'][:40]}")
    assert j['code'] == 404

    print("\n=== Test 7: 错误处理（错误日期格式）===")
    r = requests.get('http://127.0.0.1:10129/api/v1/forecasts',
                     params={'province': '山东', 'date': 'not-a-date'},
                     headers={'api-key': 'sk-test-power-2026'}, timeout=5)
    j = r.json()
    print(f"错误日期 code: {j['code']} | msg: {j['msg'][:40]}")
    assert j['code'] == 400

    print("\n✅ ALL TESTS PASSED")

if __name__ == '__main__':
    run_tests()
