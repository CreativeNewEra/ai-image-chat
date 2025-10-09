from unittest.mock import Mock, patch
from app import extract_from_chat, hide_toast, show_toast
from core.mode_manager import Mode


def test_extract_from_chat_with_message_dict_history():
    """Test extract_from_chat with Gradio 5 message dict format"""
    history = [
        {"role": "user", "content": "Hello there"},
        {"role": "assistant", "content": "Here is a short summary."},
        {
            "role": "assistant",
            "content": "This is a sufficiently descriptive prompt that should be extracted for generation.",
        },
    ]

    # Mock mode_manager to avoid ComfyUI dependency
    with patch('app.mode_manager') as mock_mode_manager:
        # Test case 1: Not in GENERATE mode - should auto-switch and show success toast
        mock_mode_manager.get_mode.return_value = Mode.CHAT
        mock_mode_manager.switch_to_generate.return_value = "Switched to Generate mode"

        prompt, toast = extract_from_chat(history)

        assert prompt == history[-1]["content"]
        # Should show success toast and call switch_to_generate
        mock_mode_manager.switch_to_generate.assert_called_once()
        assert toast["visible"] == True
        assert "Prompt copied and ready to generate" in toast["value"]

        # Test case 2: Already in GENERATE mode - should not auto-switch
        mock_mode_manager.reset_mock()
        mock_mode_manager.get_mode.return_value = Mode.GENERATE

        prompt, toast = extract_from_chat(history)

        assert prompt == history[-1]["content"]
        # Should not call switch_to_generate when already in GENERATE mode
        mock_mode_manager.switch_to_generate.assert_not_called()
        assert toast == hide_toast()
