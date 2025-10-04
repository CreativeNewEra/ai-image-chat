from app import extract_from_chat, hide_toast, mode_manager
from core.mode_manager import Mode


def test_extract_from_chat_with_message_dict_history():
    history = [
        {"role": "user", "content": "Hello there"},
        {"role": "assistant", "content": "Here is a short summary."},
        {
            "role": "assistant",
            "content": "This is a sufficiently descriptive prompt that should be extracted for generation.",
        },
    ]

    previous_mode = mode_manager.get_mode()
    try:
        mode_manager.current_mode = Mode.GENERATE
        prompt, toast = extract_from_chat(history)
    finally:
        mode_manager.current_mode = previous_mode

    assert prompt == history[-1]["content"]
    assert toast == hide_toast()
