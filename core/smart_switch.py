"""
Smart Mode Switching Module

Manages intelligent suggestions for mode switching based on user actions.
"""

import logging

logger = logging.getLogger(__name__)


class SmartSwitchManager:
    """Manage auto-switch suggestions based on user actions"""

    def __init__(self):
        self.auto_switch_enabled = True  # User preference
        self.last_action = None

    def should_suggest_switch(self, action, current_mode, active_chat_tab=None):
        """Determine if we should suggest a mode switch"""
        if not self.auto_switch_enabled:
            return None

        # Import here to avoid circular dependency
        from .mode_manager import Mode

        # After prompt extracted in chat → suggest Generate
        if action == "prompt_extracted" and current_mode == Mode.CHAT:
            return "generate"

        # After image generated → suggest Vision Chat
        if action == "image_generated" and current_mode == Mode.GENERATE:
            return "vision"

        # After vision refinement → suggest Generate (Vision tab lives under Chat mode)
        if action == "vision_refinement" and current_mode == Mode.CHAT:
            if self._is_vision_tab(active_chat_tab):
                return "generate"

        return None

    @staticmethod
    def _is_vision_tab(active_chat_tab):
        """Determine if the active chat tab represents the Vision chat interface."""
        if active_chat_tab is None:
            # When the caller doesn't provide tab info, fall back to previous behaviour
            return True

        # Gradio tab components may return either an index or label depending on context
        if isinstance(active_chat_tab, int):
            return active_chat_tab == 1
        if isinstance(active_chat_tab, float):
            return active_chat_tab.is_integer() and int(active_chat_tab) == 1
        if isinstance(active_chat_tab, str):
            normalized = active_chat_tab.strip().lower()
            if not normalized:
                return False
            if "vision" in normalized:
                return True
            if normalized in {"1", "tab_1", "vision_tab"}:
                return True

        return False

    def get_suggestion_message(self, suggested_mode):
        """Get user-friendly suggestion message"""
        if suggested_mode == "generate":
            return "💡 **Prompt ready!** Switch to Generate mode to create your image?"
        elif suggested_mode == "vision":
            return "💡 **Image created!** Switch to Vision Chat to analyze and refine it?"
        elif suggested_mode == "chat":
            return "💡 **Ready for new ideas?** Switch to Text Chat for a fresh start?"
        return ""

    def toggle_auto_switch(self):
        """Toggle auto-switch preference"""
        self.auto_switch_enabled = not self.auto_switch_enabled
        return self.auto_switch_enabled
