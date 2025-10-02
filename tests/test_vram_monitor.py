import sys
import types

import pytest

dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda *args, **kwargs: None
sys.modules.setdefault("dotenv", dotenv_stub)

from core.vram_monitor import VRAMMonitor  # noqa: E402 - Import after module stub


class DummyCompletedProcess:
    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode


def test_get_vram_usage_handles_multi_line_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monitor = VRAMMonitor()

    def fake_run(*args, **kwargs):
        return DummyCompletedProcess("500,1000\n600,1200\n")

    monkeypatch.setattr("core.vram_monitor.subprocess.run", fake_run)

    result = monitor.get_vram_usage()

    assert result == {
        "used_gb": pytest.approx(round(500 / 1024, 1)),
        "total_gb": pytest.approx(round(1000 / 1024, 1)),
        "percentage": pytest.approx(round((500 / 1000) * 100, 1)),
        "available": True,
    }


def test_get_vram_usage_returns_unavailable_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monitor = VRAMMonitor()

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("nvidia-smi not found")

    monkeypatch.setattr("core.vram_monitor.subprocess.run", fake_run)

    result = monitor.get_vram_usage()

    assert result == {"used_gb": 0, "total_gb": 16, "percentage": 0, "available": False}
