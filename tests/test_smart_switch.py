import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.mode_manager import Mode
from core.smart_switch import SmartSwitchManager


def test_vision_refinement_suggests_generate_in_chat_mode():
    manager = SmartSwitchManager()

    suggestion = manager.should_suggest_switch("vision_refinement", Mode.CHAT)

    assert suggestion == "generate"
