"""
UI Component: Mode Selector

This module provides the mode selection interface for the AI Image Chat application.
Extracted from app.py for better maintainability.
"""

import gradio as gr


def create_mode_selector() -> tuple[gr.Radio, gr.Markdown, gr.Button, gr.Checkbox, gr.Accordion]:
    """
    Create the mode selector UI component with status display.

    This component includes:
    - Mode selection radio buttons (Idle, Chat, Generate)
    - Status markdown display showing current mode and VRAM info
    - Refresh status button
    - Smart suggestions checkbox for auto-suggesting next steps
    - Keyboard shortcuts accordion (currently disabled)

    Returns
    -------
    tuple[gr.Radio, gr.Markdown, gr.Button, gr.Checkbox, gr.Accordion]
        A tuple containing:
        - mode_radio: Radio button group for mode selection
        - mode_status: Markdown display for status messages
        - check_status_btn: Button to refresh status
        - auto_switch_checkbox: Checkbox for smart suggestions
        - shortcuts_help: Accordion for keyboard shortcuts (currently not visible)

    Examples
    --------
    >>> mode_radio, mode_status, check_btn, auto_switch, shortcuts = create_mode_selector()
    >>> # Wire up event handlers in main app
    >>> mode_radio.change(fn=on_mode_change, inputs=[mode_radio], outputs=[mode_status])

    Notes
    -----
    - This component is designed to work with the ModeManager class from core.mode_manager
    - The status display should be updated when mode changes or VRAM changes
    - Keyboard shortcuts are currently disabled (visible=False) due to known issues
    - The smart suggestions feature integrates with SmartSwitchManager
    """
    with gr.Row():
        with gr.Column(scale=3, elem_classes=["mode-switcher-container"]):
            gr.Markdown("### 🎛️ Mode Control")

            mode_radio = gr.Radio(
                choices=["🔵 Idle", "💬 Chat", "🎨 Generate"],
                value="🔵 Idle",
                label="",
                elem_classes=["mode-radio-group"],
                interactive=True,
            )

            # Status and VRAM inline
            # Note: Initial value should be set by calling mode_manager._get_status_message()
            # in the main app before creating the interface
            mode_status = gr.Markdown(value="", elem_classes=["vram-display"])

            with gr.Row():
                check_status_btn = gr.Button("🔄 Refresh Status", size="sm", scale=1)
                auto_switch_checkbox = gr.Checkbox(
                    value=True,
                    label="💡 Smart Suggestions",
                    info="Auto-suggest next steps",
                    scale=2,
                )

    # Keyboard shortcuts help (collapsible)
    # Currently disabled due to known issues with button click interference
    # See TROUBLESHOOTING.md Issue #1
    with gr.Accordion("⌨️ Keyboard Shortcuts", open=False, visible=False) as shortcuts_help:
        gr.Markdown(
            """
### Mode Switching
- `Alt+I` - Switch to Idle mode
- `Alt+C` - Switch to Chat mode (use tabs for Text/Vision)
- `Alt+G` - Switch to Generate mode

### Actions
- `Ctrl+Enter` - Send chat message (when focused on message box)
- `Ctrl+G` - Generate image
- `Ctrl+K` - Copy prompt to clipboard
- `Ctrl+L` - Use last seed
- `Ctrl+Shift+C` - Clear chat

### Navigation
- `Tab` - Move between fields
- `Shift+Tab` - Move backwards between fields
            """
        )

    return mode_radio, mode_status, check_status_btn, auto_switch_checkbox, shortcuts_help
