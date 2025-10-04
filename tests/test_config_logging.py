import importlib
import sys
from pathlib import Path


def test_config_creates_missing_log_dir(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    monkeypatch.setenv("LOG_DIR", str(log_dir))
    sys.modules.pop("config", None)

    config = importlib.import_module("config")

    assert isinstance(config.LOG_DIR, Path)
    assert config.LOG_DIR == log_dir
    assert log_dir.exists()
