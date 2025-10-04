"""
Mode switching event handlers.

This module contains event handlers for mode switching functionality.
"""

import logging

import gradio as gr

from core import Mode

logger = logging.getLogger(__name__)


def handle_mode_change(mode_choice, mode_manager, vram_monitor):
    """
    Handle mode change from radio button with visual indicators and UI visibility.

    Args:
        mode_choice: Selected mode from radio button ("🔵 Idle", "💬 Chat", "🎨 Generate")
        mode_manager: ModeManager instance for switching modes
        vram_monitor: VRAMMonitor instance for VRAM usage info

    Returns:
        tuple: (status, smart_suggestion, banner, tip, idle_vis, chat_vis, generate_vis, current_mode)
    """
    logger.debug(f"Mode change requested: {mode_choice}")

    # Get VRAM info
    vram = vram_monitor.get_vram_usage()
    vram_text = f"{vram['used_gb']} GB" if vram['available'] else "N/A"

    if mode_choice == "🔵 Idle":
        status = mode_manager.switch_to_idle()
        gr.Info("⚡ Switched to Idle mode - VRAM freed")
        banner = gr.update(
            value=f"🔵 **IDLE MODE** ({vram_text} VRAM)",
            elem_classes=["mode-status-banner", "mode-idle"]
        )
        tip = gr.update(
            value="💡 **Tip:** Choose Chat or Generate mode to start working",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-idle"]
        )
        # Show only idle section
        idle_vis = gr.update(visible=True)
        chat_vis = gr.update(visible=False)
        generate_vis = gr.update(visible=False)
        current_mode = "IDLE"
    elif mode_choice == "💬 Chat":
        status = mode_manager.switch_to_chat()
        gr.Info(f"💬 Chat mode activated - Model loading ({vram_text})")
        banner = gr.update(
            value=f"🟢 **CHAT MODE** ({vram_text} VRAM)",
            elem_classes=["mode-status-banner", "mode-chat"]
        )
        tip = gr.update(
            value="💡 **Tip:** Develop prompts with Text Chat, or refine images with Vision Chat",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-chat"]
        )
        # Show only chat section
        idle_vis = gr.update(visible=False)
        chat_vis = gr.update(visible=True)
        generate_vis = gr.update(visible=False)
        current_mode = "CHAT"
    elif mode_choice == "🎨 Generate":
        status = mode_manager.switch_to_generate()
        gr.Info(f"🎨 Generate mode ready - ComfyUI active ({vram_text})")
        banner = gr.update(
            value=f"🟠 **GENERATE MODE** ({vram_text} VRAM)",
            elem_classes=["mode-status-banner", "mode-generate"]
        )
        tip = gr.update(
            value="💡 **Tip:** Click generated images in Gallery to refine them with Vision Chat",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-generate"]
        )
        # Show only generate section
        idle_vis = gr.update(visible=False)
        chat_vis = gr.update(visible=False)
        generate_vis = gr.update(visible=True)
        current_mode = "GENERATE"
    else:
        status = "Unknown mode selected"
        banner = gr.update()
        tip = gr.update()
        idle_vis = gr.update()
        chat_vis = gr.update()
        generate_vis = gr.update()
        current_mode = "IDLE"

    return status, gr.update(value="", visible=False), banner, tip, idle_vis, chat_vis, generate_vis, current_mode


def toggle_auto_switch(enabled, smart_switch):
    """
    Toggle auto-switch functionality.

    Args:
        enabled: Boolean indicating if auto-switch should be enabled
        smart_switch: SmartSwitchManager instance

    Returns:
        bool: The enabled state
    """
    smart_switch.auto_switch_enabled = enabled
    return enabled
