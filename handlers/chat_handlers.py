"""
Chat event handlers.

This module contains event handlers for text chat and vision chat functionality,
including prompt extraction, history management, and import/export.
"""

import logging
import re

import gradio as gr

from core import Mode

logger = logging.getLogger(__name__)


def user_message(message, history):
    """
    Add user message to chat history.

    Args:
        message: User's message text
        history: Chat history in Gradio 5 messages format

    Returns:
        tuple: (empty_string, updated_history)
    """
    # Gradio 5 messages format: {"role": "user/assistant", "content": "..."}
    return "", history + [{"role": "user", "content": message}]


def bot_message(
    history,
    model,
    current_prompt,
    mode_manager,
    vram_monitor,
    smart_switch,
    chat_with_ollama_func,
    show_toast_func,
    hide_toast_func
):
    """
    Process user message and generate bot response in text chat.

    Args:
        history: Chat history in Gradio 5 messages format
        model: Selected Ollama model name
        current_prompt: Current prompt text
        mode_manager: ModeManager instance
        vram_monitor: VRAMMonitor instance
        smart_switch: SmartSwitchManager instance
        chat_with_ollama_func: Function to call Ollama chat API
        show_toast_func: Function to show toast notifications
        hide_toast_func: Function to hide toast notifications

    Returns:
        tuple: (updated_history, new_prompt, suggestion_update, toast_update, banner_update,
                tip_update, idle_vis, chat_vis, generate_vis, mode_state)
    """
    # Gradio 5 messages format
    if not history or not history[-1].get("content"):
        return history, current_prompt, gr.update(value="", visible=False), hide_toast_func(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    # Auto-switch to CHAT mode if needed
    toast_update = hide_toast_func()
    banner_update = gr.update()
    tip_update = gr.update()
    idle_vis = gr.update()
    chat_vis = gr.update()
    generate_vis = gr.update()
    mode_state = gr.update()

    if mode_manager.get_mode() != Mode.CHAT:
        mode_manager.switch_to_chat()
        vram = vram_monitor.get_vram_usage()
        vram_text = f"{vram['used_gb']} GB" if vram['available'] else "N/A"

        toast_update = show_toast_func("🟢 Switching to Chat Mode...", "success")
        banner_update = gr.update(
            value=f"🟢 **CHAT MODE** ({vram_text} VRAM)",
            elem_classes=["mode-status-banner", "mode-chat"]
        )
        tip_update = gr.update(
            value="💡 **Tip:** Develop prompts with Text Chat, or refine images with Vision Chat",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-chat"]
        )
        # Update UI visibility
        idle_vis = gr.update(visible=False)
        chat_vis = gr.update(visible=True)
        generate_vis = gr.update(visible=False)
        mode_state = "CHAT"

    message = history[-1]["content"]
    response = chat_with_ollama_func(message, history[:-1], model, current_prompt)
    # Update last message to include assistant response
    history[-1] = {"role": "user", "content": message}
    history.append({"role": "assistant", "content": response})

    # Try to extract prompt from response
    new_prompt = current_prompt
    prompt_extracted = False
    if len(response) > 30:
        # If response looks like a prompt (has quotes or is descriptive)
        if '"' in response:
            matches = re.findall(r'"([^"]*)"', response)
            if matches and len(matches[-1]) > 30:
                new_prompt = matches[-1]
                prompt_extracted = True
        elif len(response) > 50 and response.count(",") > 2:
            # Looks like a detailed prompt
            new_prompt = response
            prompt_extracted = True

    # Check for smart switch suggestion
    suggestion_update = gr.update(value="", visible=False)
    if prompt_extracted:
        suggested = smart_switch.should_suggest_switch(
            "prompt_extracted", mode_manager.get_mode()
        )
        if suggested:
            suggestion_msg = smart_switch.get_suggestion_message(suggested)
            suggestion_update = gr.update(value=suggestion_msg, visible=True)

    return history, new_prompt, suggestion_update, toast_update, banner_update, tip_update, idle_vis, chat_vis, generate_vis, mode_state


def vision_user_message(message, history):
    """
    Add user message to vision chat history.

    Args:
        message: User's message text
        history: Vision chat history in Gradio 5 messages format

    Returns:
        tuple: (empty_string, updated_history)
    """
    # Gradio 5 messages format
    return "", history + [{"role": "user", "content": message}]


def vision_bot_message(history, current_image, current_prompt, vision_chat_with_ollama_func):
    """
    Process user message and generate bot response in vision chat.

    Args:
        history: Vision chat history in Gradio 5 messages format
        current_image: Current image for vision analysis
        current_prompt: Current prompt text
        vision_chat_with_ollama_func: Function to call Ollama vision chat API

    Returns:
        tuple: (updated_history, new_prompt)
    """
    # Gradio 5 messages format
    if not history or not history[-1].get("content"):
        return history, current_prompt

    message = history[-1]["content"]
    response = vision_chat_with_ollama_func(message, history[:-1], current_image, current_prompt)
    # Update last message to include assistant response
    history[-1] = {"role": "user", "content": message}
    history.append({"role": "assistant", "content": response})

    # Try to extract prompt from response
    new_prompt = current_prompt
    if len(response) > 30:
        # If response looks like a prompt (has quotes or is descriptive)
        if '"' in response:
            matches = re.findall(r'"([^"]*)"', response)
            if matches and len(matches[-1]) > 30:
                new_prompt = matches[-1]
        elif len(response) > 50 and response.count(",") > 2:
            # Looks like a detailed prompt
            new_prompt = response

    return history, new_prompt


def extract_from_chat(history, mode_manager, show_toast_func, hide_toast_func):
    """
    Extract last prompt from chat history.

    Args:
        history: Chat history
        mode_manager: ModeManager instance
        show_toast_func: Function to show toast notifications
        hide_toast_func: Function to hide toast notifications

    Returns:
        tuple: (extracted_prompt, toast_update)
    """
    if not history:
        return "No chat history to extract from!", hide_toast_func()

    # Get last assistant message
    for h in reversed(history):
        if h[1] and len(h[1]) > 30:
            # Auto-switch to GENERATE mode when extracting prompt
            if mode_manager.get_mode() != Mode.GENERATE:
                mode_manager.switch_to_generate()
                toast = show_toast_func("✅ Prompt copied and ready to generate!", "success")
                return h[1], toast
            return h[1], hide_toast_func()

    return "No suitable prompt found in chat history", hide_toast_func()


def load_selected_prompt(selected, prompt_history):
    """
    Load selected prompt from history.

    Args:
        selected: Selected prompt display text
        prompt_history: PromptHistory instance

    Returns:
        str: Full prompt text
    """
    if not selected:
        return ""
    full_prompt = prompt_history.get_prompt_by_display_text(selected)
    return full_prompt


def search_and_update_dropdown(query, prompt_history):
    """
    Search prompts and update dropdown.

    Args:
        query: Search query text
        prompt_history: PromptHistory instance

    Returns:
        gr.update: Dropdown update with search results
    """
    if not query:
        choices = prompt_history.get_dropdown_choices()
    else:
        results = prompt_history.search_prompts(query)
        choices = []
        for entry in results[:10]:
            prompt = entry["prompt"]
            if len(prompt) > 60:
                prompt = prompt[:60] + "..."
            use_info = f" ({entry['use_count']}x)" if entry.get("use_count", 1) > 1 else ""
            choices.append(f"{prompt}{use_info}")

    return gr.update(choices=choices)


def refresh_history(prompt_history):
    """
    Refresh prompt history dropdown.

    Args:
        prompt_history: PromptHistory instance

    Returns:
        gr.update: Dropdown update with current choices
    """
    return gr.update(choices=prompt_history.get_dropdown_choices())


def export_history(prompt_history):
    """
    Export prompt history.

    Args:
        prompt_history: PromptHistory instance

    Returns:
        tuple: (status_message, visible_update)
    """
    msg = prompt_history.export_prompts()
    return msg, gr.update(visible=True)


def import_history(filepath, prompt_history):
    """
    Import prompt history from file.

    Args:
        filepath: Path to history file
        prompt_history: PromptHistory instance

    Returns:
        tuple: (status_message, visible_update, dropdown_update)
    """
    if not filepath:
        return "❌ No file selected", gr.update(visible=True), gr.update()

    msg = prompt_history.import_prompts(filepath)
    choices = prompt_history.get_dropdown_choices()
    return msg, gr.update(visible=True), gr.update(choices=choices)
