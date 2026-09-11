"""Small configuration helper for the renovated application."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


import sys
from pathlib import Path

import yaml


def _get_config_path() -> Path:
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        internal_cfg = exe_dir / "_internal" / "config.yaml"
        if internal_cfg.exists():
            return internal_cfg
        return exe_dir / "config.yaml"
    return Path(__file__).resolve().parent / "config.yaml"


CONFIG_PATH = _get_config_path()


def load_config() -> dict:
    cfg_file = _get_config_path()
    values = {}
    if cfg_file.exists():
        try:
            values = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            values = {}
    values.setdefault("theme_mode", "dark")
    values.setdefault("sql_server", os.getenv("AGRIFARM_SQL_SERVER", "IT-Tauheed"))
    values.setdefault("sql_database", os.getenv("AGRIFARM_SQL_DATABASE", "AgriFarm"))
    return values


def save_config(values: dict) -> None:
    cfg_file = _get_config_path()
    try:
        cfg_file.write_text(yaml.safe_dump(values, sort_keys=True), encoding="utf-8")
    except Exception:
        pass
