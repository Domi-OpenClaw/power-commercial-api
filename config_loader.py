# -*- coding: utf-8 -*-
"""配置加载器 - 统一读取 config.yaml"""
import os
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

_config = None

def get(key: str = None, default=None):
    """按点分隔路径读取配置，如 get('security.api_key')"""
    global _config
    if _config is None:
        _config = load_config()
    if key is None:
        return _config
    keys = key.split(".")
    val = _config
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val
