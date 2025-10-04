"""
AI Image Chat - Main Application
Phase 2: Text Chat + Vision Chat + ComfyUI Generation with Mode Switching
"""

import logging
import random
import time
from datetime import datetime
from urllib.parse import urljoin

import gradio as gr
import requests

from comfyui_api import comfy

# Local imports
from config import *
from core import (
    GenerationQueue,
    ImageGallery,
    JobStatus,
    Mode,
    ModeManager,
    PromptComposer,
    PromptHistory,
    SeedManager,
    SessionStats,
    SmartSwitchManager,
    ThemeManager,
    VRAMEstimator,
    VRAMMonitor,
    WorkflowManager,
)
from ui.components import (
    create_chat_interface,
    create_gallery_view,
    create_generation_controls,
    create_generation_settings,
    create_queue_panel,
    create_mode_selector,
    create_prompt_composer,
    create_theme_settings,
)
from utils import pil_to_base64

# Import handlers
from handlers import (
    # Mode handlers
    handle_mode_change as _handle_mode_change,
    toggle_auto_switch as _toggle_auto_switch,
    # Gallery handlers
    update_gallery_display as _update_gallery_display,
    show_gallery_stats as _show_gallery_stats,
    load_gallery_image as _load_gallery_image,
    open_gallery as _open_gallery,
    close_gallery as _close_gallery,
    gallery_toggle_favorite as _gallery_toggle_favorite,
    gallery_use_img2img as _gallery_use_img2img,
    gallery_open_vision as _gallery_open_vision,
    gallery_delete_image as _gallery_delete_image,
    # Workflow handlers
    get_workflow_info_display as _get_workflow_info_display,
    switch_workflow as _switch_workflow,
    refresh_workflows as _refresh_workflows,
    filter_workflows_by_category as _filter_workflows_by_category,
    import_workflow_from_file as _import_workflow_from_file,
    export_current_workflow as _export_current_workflow,
    # Chat handlers
    user_message as _user_message,
    bot_message as _bot_message,
    vision_user_message as _vision_user_message,
    vision_bot_message as _vision_bot_message,
    load_selected_prompt as _load_selected_prompt,
    search_and_update_dropdown as _search_and_update_dropdown,
    refresh_history as _refresh_history,
    export_history as _export_history,
    import_history as _import_history,
    # Generation handlers
    apply_preset as _apply_preset,
    update_warnings_from_sliders as _update_warnings_from_sliders,
    use_last_seed as _use_last_seed,
    adjust_seed as _adjust_seed,
    random_seed as _random_seed,
    toggle_seed_lock as _toggle_seed_lock,
    select_from_history as _select_from_history,
    update_seed_history as _update_seed_history,
    generate_and_store as _generate_and_store,
    start_seed_variations as _start_seed_variations,
    refine_in_vision as _refine_in_vision,
    toggle_favorite_generated as _toggle_favorite_generated,
    copy_seed_to_clipboard as _copy_seed_to_clipboard,
    # UI handlers
    get_enhanced_progress_html as _get_enhanced_progress_html,
    toggle_shortcuts as _toggle_shortcuts,
    open_settings as _open_settings,
    close_settings as _close_settings,
    apply_theme as _apply_theme,
    reset_theme as _reset_theme,
    open_composer as _open_composer,
    close_composer as _close_composer,
    add_tag_to_composer as _add_tag_to_composer,
    build_from_tags as _build_from_tags,
    clear_all_tags as _clear_all_tags,
    load_template_handler as _load_template_handler,
    copy_to_main_prompt as _copy_to_main_prompt,
    save_custom_template as _save_custom_template,
    open_image_preview as _open_image_preview,
    close_image_preview as _close_image_preview,
)

# Get logger for this module
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Initialize all core components
vram_monitor = VRAMMonitor()
session_stats = SessionStats()
vram_estimator = VRAMEstimator()
seed_manager = SeedManager()
prompt_history = PromptHistory(PROMPT_HISTORY_FILE)
smart_switch = SmartSwitchManager()
gallery = ImageGallery()
gen_queue = GenerationQueue()
workflow_manager = WorkflowManager()
theme_manager = ThemeManager()
prompt_composer = PromptComposer()

# Toast notification helpers (available globally for reuse and testing)


def show_toast(message, toast_type="info"):
    """Show a toast notification (returns update for toast component)."""

    toast_class = f"toast toast-{toast_type}"
    return gr.update(value=f"**{message}**", visible=True, elem_classes=[toast_class])


def hide_toast():
    """Hide toast notification."""

    return gr.update(value="", visible=False)


def _extract_text_content(content):
    """Normalize message content to a string for prompt extraction."""

    if isinstance(content, str):
        return content

    if isinstance(content, dict):
        # Gradio can represent complex content as dictionaries (e.g., {"text": "..."}).
        text = content.get("text")
        return text if isinstance(text, str) else ""

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return " ".join(parts)

    return str(content) if content is not None else ""


def extract_from_chat(history):
    """
    Extract the most recent assistant prompt from chat history.

    Args:
        history (list): The chat history. Supported formats:
            - List of dicts: Each dict should have at least a "role" key (e.g., "assistant") and a "content" key.
            - List of tuples/lists: Each entry is a (user, assistant) tuple or list, where the assistant's response is at index 1.

    Returns:
        tuple: (content_text, toast)
            - content_text (str): The extracted assistant prompt, or an error message if not found.
            - toast (gradio.Update): A Gradio update object for showing or hiding a toast notification.

    Notes:
        - If the most recent assistant prompt is found and is longer than 30 characters, the function may trigger a mode switch to GENERATE and show a success toast.
        - If no suitable prompt is found, an error message and a hidden toast are returned.
    """
    if not history:
        return "No chat history to extract from!", hide_toast()

    for entry in reversed(history):
        content_text = ""

        if isinstance(entry, dict):
            if entry.get("role") != "assistant":
                continue
            content_text = _extract_text_content(entry.get("content"))
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            # Legacy Gradio history stored as (user, assistant)
            assistant_response = entry[1]
            if assistant_response is None:
                continue
            content_text = assistant_response if isinstance(assistant_response, str) else str(assistant_response)
        else:
            continue

        if content_text and len(content_text) > 30:
            if mode_manager.get_mode() != Mode.GENERATE:
                mode_manager.switch_to_generate()
                toast = show_toast("✅ Prompt copied and ready to generate!", "success")
                return content_text, toast

            return content_text, hide_toast()

    return "No suitable prompt found in chat history", hide_toast()

# Set default workflow (prefer text2img)
if not workflow_manager.get_current_workflow() and workflow_manager.get_workflow_count() > 0:
    # Try to find a text2img workflow first
    text2img_workflow = None
    for workflow_id, workflow in workflow_manager.workflows.items():
        if workflow.metadata.matches_category("text2img"):
            text2img_workflow = workflow_id
            break

    # Use text2img if found, otherwise use first available
    default_workflow = text2img_workflow or list(workflow_manager.workflows.keys())[0]
    workflow_manager.set_current_workflow(default_workflow)
    logger.info(
        f"Auto-selected default workflow: {workflow_manager.get_current_workflow().metadata.name}"
    )

# Mode manager needs vram_monitor and comfy
mode_manager = ModeManager(vram_monitor, comfy)

# ============================================================================
# OLLAMA CHAT
# ============================================================================


def _build_ollama_tags_url(base_url: str) -> str:
    """Construct the Ollama tags endpoint from the configured API URL."""
    trimmed = base_url.rstrip("/")
    if trimmed.endswith("/api"):
        trimmed = trimmed[:-4]
    return urljoin(trimmed + "/", "api/tags")


def get_available_models():
    """Get list of Ollama models"""
    try:
        response = requests.get(_build_ollama_tags_url(OLLAMA_API))
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
    except Exception:
        pass
    return [OLLAMA_CHAT_MODEL, "mistral:7b", "mistral-small3.2:latest"]


def chat_with_ollama(message, history, model_choice, current_prompt):
    """Send message to Ollama and get response"""

    if mode_manager.get_mode() != Mode.CHAT:
        return "⚠️ Please switch to Text Chat Mode first!"

    try:
        # Build message history
        # Gradio 5 uses 'messages' format with 'role' and 'content' keys
        messages = []
        for h in history:
            # History is already in messages format: {"role": "user/assistant", "content": "..."}
            if isinstance(h, dict) and "role" in h and "content" in h:
                messages.append(h)
            # Fallback for old tuple format (backwards compatibility)
            elif isinstance(h, (list, tuple)) and len(h) >= 2:
                messages.append({"role": "user", "content": h[0]})
                if h[1]:
                    messages.append({"role": "assistant", "content": h[1]})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Add context about current prompt
        context = ""
        if current_prompt:
            context = f"\n\nCurrent working prompt: '{current_prompt}'\n"

        # Call Ollama
        response = requests.post(
            f"{OLLAMA_API}/chat",
            json={
                "model": model_choice,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT + context}] + messages,
                "stream": False,
                "keep_alive": "5m",
            },
            timeout=60,
        )

        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error: {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


def vision_chat_with_ollama(message, history, current_image, current_prompt):
    """Send message with image to Ollama vision model and get response"""

    if mode_manager.get_mode() != Mode.CHAT:
        return "⚠️ Please switch to Chat Mode first!"

    if current_image is None:
        return "⚠️ No image loaded! Generate an image first, then click on it in the gallery."

    try:
        # Convert image to base64
        image_base64 = pil_to_base64(current_image)
        if not image_base64:
            return "⚠️ Failed to process image"

        # Build message history (text only for history)
        # Gradio 5 uses 'messages' format with 'role' and 'content' keys
        messages = []
        for h in history:
            # History is already in messages format
            if isinstance(h, dict) and "role" in h and "content" in h:
                # Remove images from history (only current message has image)
                msg = {"role": h["role"], "content": h["content"]}
                messages.append(msg)
            # Fallback for old tuple format
            elif isinstance(h, (list, tuple)) and len(h) >= 2:
                messages.append({"role": "user", "content": h[0]})
                if h[1]:
                    messages.append({"role": "assistant", "content": h[1]})

        # Add current message with image
        messages.append({"role": "user", "content": message, "images": [image_base64]})

        # Add context about current prompt
        context = ""
        if current_prompt:
            context = f"\n\nCurrent image generation prompt: '{current_prompt}'\n"

        # Call Ollama with vision model
        response = requests.post(
            f"{OLLAMA_API}/chat",
            json={
                "model": OLLAMA_VISION_MODEL,
                "messages": [{"role": "system", "content": VISION_SYSTEM_PROMPT + context}]
                + messages,
                "stream": False,
                "keep_alive": "5m",
            },
            timeout=120,  # Vision models may take longer
        )

        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error: {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# IMAGE GENERATION
# ============================================================================


def check_vram_warnings(steps, width, height):
    """Check VRAM warnings and return display markdown"""
    vram_info = vram_monitor.get_vram_usage()
    current_used = vram_info["used_gb"]
    total_vram = vram_info["total_gb"]

    warning_level, warning_msg = vram_estimator.get_warnings(
        width, height, steps, current_used, total_vram
    )

    # Return tuple: (markdown_text, visible_boolean)
    if warning_level == "none":
        return "", False
    elif warning_level == "info":
        return f"ℹ️ {warning_msg}", True
    elif warning_level == "warning":
        return f"⚠️ {warning_msg}", True
    elif warning_level == "error":
        return f"🚨 {warning_msg}", True
    else:
        return "", False


def generate_image(
    prompt_text, steps, width, height, seed_value, denoise=1.0, input_image_path=None
):
    """Generate image via ComfyUI (text2img or img2img)

    Args:
        prompt_text: The text prompt
        steps: Number of sampling steps
        width: Image width (text2img only)
        height: Image height (text2img only)
        seed_value: Random seed value as string
        denoise: Denoising strength (0.0-1.0, for img2img)
        input_image_path: Path to input image (for img2img, None for text2img)

    Returns:
        tuple: (image, status, actual_seed, stats_display)
    """

    if mode_manager.get_mode() != Mode.GENERATE:
        return None, "⚠️ Please switch to Generation Mode first!", None, None

    # Validate prompt
    if not prompt_text or len(prompt_text) < MIN_PROMPT_LENGTH:
        return (
            None,
            f"⚠️ Please provide a prompt (at least {MIN_PROMPT_LENGTH} characters)",
            None,
            None,
        )

    # Validate width/height only for text2img
    if not input_image_path:
        if not (MIN_WIDTH <= width <= MAX_WIDTH):
            return None, f"❌ Width must be between {MIN_WIDTH} and {MAX_WIDTH} pixels", None, None
        if not (MIN_HEIGHT <= height <= MAX_HEIGHT):
            return (
                None,
                f"❌ Height must be between {MIN_HEIGHT} and {MAX_HEIGHT} pixels",
                None,
                None,
            )

    # Validate steps
    if not (MIN_STEPS <= steps <= MAX_STEPS):
        return None, f"❌ Steps must be between {MIN_STEPS} and {MAX_STEPS}", None, None

    # Log mode
    mode_str = "img2img" if input_image_path else "text2img"
    logger.info(f"Generating image ({mode_str}): {width}x{height}, {steps} steps")
    if input_image_path:
        logger.info(f"Input image: {input_image_path}, denoise: {denoise}")

    # Auto-select correct workflow based on generation mode
    required_category = "img2img" if input_image_path else "text2img"
    current_workflow = workflow_manager.get_current_workflow()

    # If current workflow doesn't match required category, find the right one
    if (
        not current_workflow
        or not current_workflow.metadata.matches_category(required_category)
    ):
        logger.info(f"Searching for {required_category} workflow...")
        for workflow_id, workflow in workflow_manager.workflows.items():
            if workflow.metadata.matches_category(required_category):
                workflow_manager.set_current_workflow(workflow_id)
                current_workflow = workflow
                logger.info(f"Auto-selected {required_category} workflow: {workflow.metadata.name}")
                break

        if (
            not current_workflow
            or not current_workflow.metadata.matches_category(required_category)
        ):
            return None, f"❌ No {required_category} workflow available. Please add one to workflows/{required_category}/", None, None

    # Load workflow data into ComfyUI bridge (reload every time)
    logger.info(f"Using workflow: {current_workflow.metadata.name} ({current_workflow.metadata.category})")
    if not comfy.load_workflow_from_data(current_workflow.workflow_data):
        return None, "❌ Failed to load workflow", None, None

    # Parse seed
    seed = None
    if seed_value and seed_value.strip():
        try:
            seed = int(seed_value)
        except ValueError:
            logger.warning(f"Invalid seed input '{seed_value}'; using managed default")
            seed = None

    # Check if seed is locked
    seed = seed_manager.get_seed_for_generation(seed)

    # Track generation time
    start_time = time.time()

    # Generate
    image, status, actual_seed = comfy.generate_image(
        prompt_text=prompt_text,
        steps=steps,
        width=width,
        height=height,
        seed=seed,
        denoise=denoise,
        input_image_path=input_image_path,
    )

    # Calculate generation time
    generation_time = time.time() - start_time

    # If generation succeeded, save to gallery and record stats
    if image is not None and actual_seed is not None:
        settings = {"width": width, "height": height, "steps": steps}

        gallery.add_image(image, prompt_text, actual_seed, settings)

        # Record generation stats
        session_stats.add_generation(generation_time)

        # Add seed to history
        seed_manager.add_seed(actual_seed)

        # Add prompt to history
        prompt_history.add_prompt(prompt_text, settings)

        # Show success notification
        gr.Info(f"✨ Image generated in {round(generation_time, 1)}s (Seed: {actual_seed})")

        # Return seed info and time in status
        lock_status = " 🔒 LOCKED" if seed_manager.is_locked else ""
        status = (
            f"{status}\n\nSeed: {actual_seed}{lock_status} | Time: {round(generation_time, 1)}s"
        )
    else:
        # Show error notification on failure
        gr.Error("Failed to generate image - check ComfyUI status")

    # Return stats display as 4th value
    stats_display = session_stats.get_stats_display()

    return image, status, actual_seed, stats_display


# ============================================================================
# BATCH GENERATION QUEUE
# ============================================================================


def add_to_queue(prompt_text, steps, width, height, seed_value):
    """Add current settings to generation queue"""
    if not prompt_text or len(prompt_text) < MIN_PROMPT_LENGTH:
        return (
            f"⚠️ Please provide a prompt (at least {MIN_PROMPT_LENGTH} characters)",
            gen_queue.get_queue_display(),
        )

    # Parse seed
    seed = -1  # -1 means random
    if seed_value and seed_value.strip():
        try:
            seed = int(seed_value)
        except ValueError:
            logger.warning(f"Invalid seed input '{seed_value}'; using random seed")
            seed = -1

    job_id = gen_queue.add_job(prompt_text, width, height, steps, seed)
    logger.info(f"Added job {job_id} to queue")
    gr.Info(f"Added to queue (Job #{job_id[-4:]})")

    return f"✅ Added to queue (Job #{job_id[-4:]})", gen_queue.get_queue_display()


def add_batch_variations(prompt_text, steps, width, height, seed_value, count=4):
    """Add batch of seed variations to queue"""
    if not prompt_text or len(prompt_text) < MIN_PROMPT_LENGTH:
        return (
            f"⚠️ Please provide a prompt (at least {MIN_PROMPT_LENGTH} characters)",
            gen_queue.get_queue_display(),
        )

    # Parse seed
    seed = None
    if seed_value and seed_value.strip():
        try:
            seed = int(seed_value)
        except ValueError:
            logger.warning(
                f"Invalid seed input '{seed_value}'; using history/random fallback"
            )
            seed = None

    # If no seed provided, use last seed from history or generate random
    if seed is None or seed == -1:
        history = seed_manager.get_history()
        if history:
            seed = history[0]  # Use most recent seed
        else:
            seed = random.randint(0, 2**32 - 1)

    job_ids = gen_queue.add_batch_variations(prompt_text, width, height, steps, seed, count)
    logger.info(f"Added {count} variation jobs to queue")
    gr.Info(f"🎲 Added {count} seed variations to queue")

    return (
        f"✅ Added {count} seed variations to queue (seed {seed} +1, +2, +3...)",
        gen_queue.get_queue_display(),
    )


def process_queue():
    """Process all jobs in the queue"""
    if mode_manager.get_mode() != Mode.GENERATE:
        return (
            None,
            "⚠️ Please switch to Generation Mode first!",
            gen_queue.get_queue_display(),
            None,
        )

    next_job = gen_queue.get_next_job()
    if not next_job:
        return None, "Queue is empty", gen_queue.get_queue_display(), None

    # Mark as processing
    next_job.status = JobStatus.PROCESSING
    gen_queue.current_job = next_job
    next_job.started_at = datetime.now()

    logger.info(f"Processing job {next_job.id}: {next_job.prompt[:50]}...")

    # Track generation time
    start_time = time.time()

    # Generate
    image, status, actual_seed = comfy.generate_image(
        prompt_text=next_job.prompt,
        steps=next_job.steps,
        width=next_job.width,
        height=next_job.height,
        seed=next_job.seed if next_job.seed != -1 else None,
    )

    generation_time = time.time() - start_time

    # Update job status
    next_job.completed_at = datetime.now()

    if image is not None and actual_seed is not None:
        # Success
        next_job.status = JobStatus.COMPLETED
        next_job.result_image = image
        next_job.result_seed = actual_seed

        # Save to gallery
        settings = {"width": next_job.width, "height": next_job.height, "steps": next_job.steps}
        gallery.add_image(image, next_job.prompt, actual_seed, settings)

        # Record stats
        session_stats.add_generation(generation_time)
        seed_manager.add_seed(actual_seed)
        prompt_history.add_prompt(next_job.prompt, settings)

        status = f"✅ Job completed\nSeed: {actual_seed} | Time: {round(generation_time, 1)}s\n{gen_queue.get_queue_display()}"
    else:
        # Failed
        next_job.status = JobStatus.FAILED
        next_job.error_message = status
        status = f"❌ Job failed: {status}\n{gen_queue.get_queue_display()}"

    gen_queue.current_job = None
    stats_display = session_stats.get_stats_display()

    return image, status, gen_queue.get_queue_display(), stats_display


def clear_queue():
    """Clear all completed jobs from queue"""
    gen_queue.clear_completed()
    return gen_queue.get_queue_display()


def cancel_all_queue():
    """Cancel all pending jobs"""
    gen_queue.clear_all()
    return gen_queue.get_queue_display()


# ============================================================================
# GRADIO INTERFACE
# ============================================================================


def create_app():
    """Create Gradio UI"""

    # ============================================================================
    # EXTERNAL JAVASCRIPT MODULES
    # ============================================================================
    # JavaScript code has been extracted to static/js/ for better organization:
    # - static/js/main.js: Entry point, imports and initializes all modules
    # - static/js/toast.js: Toast notification system
    # - static/js/keyboard_shortcuts.js: Keyboard shortcuts (with stopPropagation fix)
    #
    # The main.js module is loaded as an ES6 module, which allows proper imports.
    # It makes showToast() globally available for Gradio's inline JS callbacks.
    # JavaScript is disabled for now - Gradio 5 changed static file serving
    # Keyboard shortcuts will be re-implemented in a future update
    # custom_js = """
    # // Load external JavaScript modules
    # import('/file=static/js/main.js');
    # """

    # Load external CSS file
    custom_css = ""
    try:
        with open("static/css/styles.css", "r") as f:
            custom_css = f.read()
    except FileNotFoundError:
        logger.warning("Custom CSS file not found: static/css/styles.css")

    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue"),
        title="AI Image Chat",
        # js=custom_js,  # Disabled: Gradio 5 compatibility issue with /file= path
        css=custom_css + """
        /* ========================================
           MODE-SPECIFIC STYLES (App.py)
           ======================================== */

        /* Mode Status Banner */
        .mode-status-banner {
            padding: 16px 24px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
            border-left: 6px solid;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .mode-idle {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left-color: #2196f3;
            color: #1565c0;
        }

        .mode-chat {
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left-color: #4caf50;
            color: #2e7d32;
        }

        .mode-generate {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-left-color: #ff9800;
            color: #e65100;
        }

        /* Mode Status Card (legacy) */
        .mode-status {
            padding: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Section Cards */
        .section-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
        }

        .section-header {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Mode Switcher */
        .mode-switcher-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
        }

        .mode-radio-group .gr-radio {
            display: flex !important;
            flex-direction: row !important;
            gap: 12px !important;
        }

        .mode-radio-group label {
            background: #f3f4f6 !important;
            padding: 14px 24px !important;
            border-radius: 10px !important;
            border: 3px solid transparent !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-weight: 500 !important;
            font-size: 15px !important;
        }

        .mode-radio-group label:hover {
            background: #e5e7eb !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        }

        /* Active mode button - Idle */
        .mode-radio-group input[type="radio"]:checked + label[data-testid*="🔵"] {
            background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%) !important;
            color: white !important;
            border-color: #1565c0 !important;
            box-shadow: 0 6px 16px rgba(33, 150, 243, 0.4) !important;
            transform: scale(1.05);
        }

        /* Active mode button - Chat */
        .mode-radio-group input[type="radio"]:checked + label[data-testid*="💬"] {
            background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%) !important;
            color: white !important;
            border-color: #2e7d32 !important;
            box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4) !important;
            transform: scale(1.05);
        }

        /* Active mode button - Generate */
        .mode-radio-group input[type="radio"]:checked + label[data-testid*="🎨"] {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
            color: white !important;
            border-color: #e65100 !important;
            box-shadow: 0 6px 16px rgba(255, 152, 0, 0.4) !important;
            transform: scale(1.05);
        }

        /* Fallback for any active button */
        .mode-radio-group input[type="radio"]:checked + label {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-color: #667eea !important;
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
            transform: scale(1.05);
        }

        /* Mode Tips Display */
        .mode-tip {
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            margin-top: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            animation: slideInDown 0.4s ease;
        }

        .mode-tip-idle {
            background: #e3f2fd;
            color: #1565c0;
            border-left: 4px solid #2196f3;
        }

        .mode-tip-chat {
            background: #e8f5e9;
            color: #2e7d32;
            border-left: 4px solid #4caf50;
        }

        .mode-tip-generate {
            background: #fff3e0;
            color: #e65100;
            border-left: 4px solid #ff9800;
        }

        /* VRAM Display */
        .vram-display {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            padding: 12px 16px;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-top: 12px;
            transition: all 0.3s ease;
        }

        /* Mode Transition Animations */
        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        @keyframes pulseGlow {
            0%, 100% {
                box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
            }
            50% {
                box-shadow: 0 6px 24px rgba(102, 126, 234, 0.6);
            }
        }

        /* Smooth transitions for all mode elements */
        .mode-switcher-container {
            animation: fadeIn 0.5s ease;
        }

        /* Shortcuts Modal */
        .shortcuts-modal {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            font-family: monospace;
        }

        /* Smart Suggestion */
        .smart-suggestion {
            padding: 15px;
            border-radius: 8px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            font-size: 14px;
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(240, 147, 251, 0.3);
        }

        /* Preset Cards */
        .preset-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }

        .preset-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        /* Better Button Styling */
        .primary-action {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }

        .primary-action:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        }

        /* Gallery Improvements */
        .gallery-controls {
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        /* Toast Notifications */
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }

        .toast {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            min-width: 300px;
            opacity: 0;
            transform: translateX(400px);
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            pointer-events: auto;
        }

        .toast-show {
            opacity: 1;
            transform: translateX(0);
        }

        .toast-icon {
            font-size: 20px;
            flex-shrink: 0;
        }

        .toast-message {
            font-size: 14px;
            font-weight: 500;
            color: #1f2937;
        }

        .toast-success {
            border-left: 4px solid #10b981;
        }

        .toast-error {
            border-left: 4px solid #ef4444;
        }

        .toast-warning {
            border-left: 4px solid #f59e0b;
        }

        .toast-info {
            border-left: 4px solid #3b82f6;
        }

        /* Progress Bar */
        .progress-container {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            border-radius: 4px;
        }

        .progress-bar.indeterminate {
            width: 30%;
            animation: indeterminate 1.5s infinite ease-in-out;
        }

        @keyframes indeterminate {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
        }

        /* Image Action Buttons */
        .image-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .image-action-btn {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .image-action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .btn-variations {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-refine {
            background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
            color: white;
        }

        .btn-favorite {
            background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
            color: #333;
        }

        .btn-copy-seed {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
        }

        .btn-img2img {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
        }

        .btn-delete {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }

        /* Gallery Image Actions (on hover) */
        .gallery-item-wrapper {
            position: relative;
        }

        .gallery-item-actions {
            position: absolute;
            bottom: 8px;
            left: 8px;
            right: 8px;
            display: none;
            gap: 4px;
            background: rgba(0, 0, 0, 0.8);
            padding: 6px;
            border-radius: 8px;
            backdrop-filter: blur(4px);
        }

        .gallery-item-wrapper:hover .gallery-item-actions {
            display: flex;
        }

        .gallery-action-btn {
            flex: 1;
            padding: 6px;
            border-radius: 6px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }

        .gallery-action-btn:hover {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(1.1);
        }

        /* Image Preview Modal */
        .image-preview-modal {
            max-width: 90vw;
            max-height: 90vh;
        }

        .image-metadata {
            background: #f5f5f5;
            padding: 16px;
            border-radius: 8px;
            margin-top: 12px;
        }

        .metadata-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }

        .metadata-row:last-child {
            border-bottom: none;
        }

        .metadata-label {
            font-weight: 600;
            color: #555;
        }

        .metadata-value {
            color: #333;
        }
        """,
    ) as app:

        # Header
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown(
                    """
                # 🎨 AI Image Chat
                **Smart workflow for AI-assisted image generation**
                """
                )
            with gr.Column(scale=1):
                with gr.Row():
                    gallery_btn = gr.Button("📁 Gallery", size="sm", variant="primary")
                    composer_btn = gr.Button("🎨 Composer", size="sm", variant="secondary")
                    settings_btn = gr.Button("⚙️ Settings", size="sm")
                    shortcuts_btn = gr.Button("⌨️ Shortcuts", size="sm")

        # State
        current_prompt_state = gr.State("")
        current_image_state = gr.State(None)
        current_mode_state = gr.State("IDLE")  # Track current mode for UI visibility

        # ====================================================================
        # MODE SELECTOR & STATUS
        # ====================================================================
        # Extracted to ui/components/mode_selector.py for better maintainability

        (
            mode_radio,
            mode_status,
            check_status_btn,
            auto_switch_checkbox,
            shortcuts_help,
        ) = create_mode_selector()

        # Set initial status value (create_mode_selector returns empty string by default)
        mode_status.value = mode_manager._get_status_message()

        # Mode status banner with VRAM
        mode_status_banner = gr.Markdown(
            value="🔵 **IDLE MODE** (0.0 GB VRAM)",
            elem_classes=["mode-status-banner", "mode-idle"]
        )

        # Mode-specific tips
        mode_tip = gr.Markdown(
            value="💡 **Tip:** Choose a mode above to begin",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-idle"]
        )

        # Smart mode suggestion display
        smart_suggestion = gr.Markdown(value="", visible=False, elem_classes=["smart-suggestion"])

        # Toast notification component
        toast_notification = gr.Markdown(
            value="",
            visible=False,
            elem_classes=["toast", "toast-info"]
        )

        gr.Markdown("---")

        # ====================================================================
        # MAIN INTERFACE - MODE-SPECIFIC SECTIONS
        # ====================================================================

        # IDLE MODE UI
        with gr.Column(visible=True) as idle_section:
            gr.Markdown(
                """
                ## 👋 Welcome to AI Image Chat

                Choose a mode above to begin:

                - **💬 Chat Mode**: Develop prompts with Text Chat or refine images with Vision Chat
                - **🎨 Generate Mode**: Create images with ComfyUI + FLUX

                **Workflow:**
                1. Switch to Chat mode → Develop prompts with AI assistance
                2. Switch to Generate mode → Create images
                3. Click gallery images → Auto-switch to Vision Chat for refinement
                """,
                elem_classes=["section-card"]
            )

        # CHAT MODE UI
        with gr.Column(visible=False) as chat_section:
            gr.Markdown(
                '<div class="section-header">💬 AI Chat Assistant</div>',
                elem_classes=["section-card"],
            )

            # ============================================================
            # CHAT INTERFACE
            # ============================================================
            # Extracted to ui/components/chat_interface.py for better maintainability

            with gr.Tabs() as chat_tabs:
                chat_components = create_chat_interface(
                    available_models=get_available_models(), default_model=OLLAMA_CHAT_MODEL
                )

            # Extract components from dictionary for easier access
            chat_tabs = chat_components["chat_tabs"]
            model_dropdown = chat_components["model_dropdown"]
            refresh_models_btn = chat_components["refresh_models_btn"]
            chatbot = chat_components["chatbot"]
            msg = chat_components["msg"]
            send_btn = chat_components["send_btn"]
            clear_chat_btn = chat_components["clear_chat_btn"]
            vision_chatbot = chat_components["vision_chatbot"]
            vision_image_preview = chat_components["vision_image_preview"]
            vision_msg = chat_components["vision_msg"]
            vision_send_btn = chat_components["vision_send_btn"]
            clear_vision_btn = chat_components["clear_vision_btn"]

        # GENERATE MODE UI
        with gr.Column(visible=False) as generate_section:
            # ============================================================
            # GENERATION PANEL
            # ============================================================
            # Extracted to ui/components/generation_controls.py, generation_settings.py, and queue_panel.py
            # for better maintainability (split from generation_panel.py)

            # Create generation controls (prompt, presets, generate button, image display)
            gen_controls = create_generation_controls(
                prompt_history=prompt_history,
                default_config={
                    "DEFAULT_STEPS": DEFAULT_STEPS,
                    "DEFAULT_WIDTH": DEFAULT_WIDTH,
                    "DEFAULT_HEIGHT": DEFAULT_HEIGHT,
                },
            )

            # Create generation settings (parameters, workflow, statistics)
            gen_settings = create_generation_settings(
                workflow_manager=workflow_manager,
                session_stats=session_stats,
                default_config={
                    "DEFAULT_STEPS": DEFAULT_STEPS,
                    "DEFAULT_WIDTH": DEFAULT_WIDTH,
                    "DEFAULT_HEIGHT": DEFAULT_HEIGHT,
                },
            )

            # Create batch queue panel
            queue_components = create_queue_panel()

            # Extract components from dictionaries for easier access
            # From generation_controls
            quick_generate_btn = gen_controls["quick_generate_btn"]
            quick_copy_btn = gen_controls["quick_copy_btn"]
            quick_clear_btn = gen_controls["quick_clear_btn"]
            quick_extract_btn = gen_controls["quick_extract_btn"]
            prompt_display = gen_controls["prompt_display"]
            extract_prompt_btn = gen_controls["extract_prompt_btn"]
            copy_prompt_btn = gen_controls["copy_prompt_btn"]
            clear_prompt_btn = gen_controls["clear_prompt_btn"]
            prompt_search = gen_controls["prompt_search"]
            search_btn = gen_controls["search_btn"]
            prompt_history_dropdown = gen_controls["prompt_history_dropdown"]
            load_prompt_btn = gen_controls["load_prompt_btn"]
            refresh_history_btn = gen_controls["refresh_history_btn"]
            export_prompts_btn = gen_controls["export_prompts_btn"]
            import_file = gen_controls["import_file"]
            history_status = gen_controls["history_status"]
            preset_fast = gen_controls["preset_fast"]
            preset_balanced = gen_controls["preset_balanced"]
            preset_quality = gen_controls["preset_quality"]
            preset_ultra = gen_controls["preset_ultra"]
            generate_btn = gen_controls["generate_btn"]
            vram_warning_display = gen_controls["vram_warning_display"]
            generation_progress = gen_controls["generation_progress"]
            generation_status = gen_controls["generation_status"]
            generated_image = gen_controls["generated_image"]
            gen_variations_btn = gen_controls["gen_variations_btn"]
            gen_refine_btn = gen_controls["gen_refine_btn"]
            gen_favorite_btn = gen_controls["gen_favorite_btn"]
            gen_copy_seed_btn = gen_controls["gen_copy_seed_btn"]

            # From generation_settings
            steps_slider = gen_settings["steps_slider"]
            width_slider = gen_settings["width_slider"]
            height_slider = gen_settings["height_slider"]
            seed_input = gen_settings["seed_input"]
            seed_lock_checkbox = gen_settings["seed_lock_checkbox"]
            use_last_seed_btn = gen_settings["use_last_seed_btn"]
            seed_random_btn = gen_settings["seed_random_btn"]
            seed_minus_100_btn = gen_settings["seed_minus_100_btn"]
            seed_minus_10_btn = gen_settings["seed_minus_10_btn"]
            seed_minus_1_btn = gen_settings["seed_minus_1_btn"]
            seed_plus_1_btn = gen_settings["seed_plus_1_btn"]
            seed_plus_10_btn = gen_settings["seed_plus_10_btn"]
            seed_plus_100_btn = gen_settings["seed_plus_100_btn"]
            seed_history_dropdown = gen_settings["seed_history_dropdown"]
            input_image = gen_settings["input_image"]
            denoise_slider = gen_settings["denoise_slider"]
            workflow_dropdown = gen_settings["workflow_dropdown"]
            workflow_refresh_btn = gen_settings["workflow_refresh_btn"]
            workflow_category_filter = gen_settings["workflow_category_filter"]
            workflow_info = gen_settings["workflow_info"]
            workflow_upload_file = gen_settings["workflow_upload_file"]
            workflow_import_btn = gen_settings["workflow_import_btn"]
            workflow_export_btn = gen_settings["workflow_export_btn"]
            stats_display = gen_settings["stats_display"]

            # From queue_panel
            add_queue_btn = queue_components["add_queue_btn"]
            batch_variations_btn = queue_components["batch_variations_btn"]
            variation_count = queue_components["variation_count"]
            queue_status = queue_components["queue_status"]
            process_queue_btn = queue_components["process_queue_btn"]
            clear_completed_btn = queue_components["clear_completed_btn"]
            cancel_all_btn = queue_components["cancel_all_btn"]

        # ====================================================================
        # GALLERY SECTION
        # ====================================================================
        # Gallery with visibility toggle (Gradio 5 compatible)

        with gr.Accordion("📁 Session Gallery", open=False, visible=False) as gallery_modal:
            gr.Markdown("# 📁 Session Gallery")

            gallery_components = create_gallery_view()

            # Extract components from dictionary for easier access
            gallery_filter = gallery_components["gallery_filter"]
            gallery_sort = gallery_components["gallery_sort"]
            favorites_only_check = gallery_components["favorites_only_check"]
            refresh_gallery_btn = gallery_components["refresh_gallery_btn"]
            gallery_stats_btn = gallery_components["gallery_stats_btn"]
            session_gallery = gallery_components["session_gallery"]
            gallery_info = gallery_components["gallery_info"]

            # Gallery action buttons (for selected image)
            gr.Markdown("**Selected Image Actions:**")
            with gr.Row(elem_classes=["image-actions"]):
                gallery_favorite_btn = gr.Button(
                    "⭐ Toggle Favorite",
                    size="sm",
                    elem_classes=["image-action-btn", "btn-favorite"]
                )
                gallery_img2img_btn = gr.Button(
                    "🎨 Use for Img2Img",
                    size="sm",
                    elem_classes=["image-action-btn", "btn-img2img"]
                )
                gallery_vision_btn = gr.Button(
                    "👁️ Open in Vision Chat",
                    size="sm",
                    elem_classes=["image-action-btn", "btn-refine"]
                )
                gallery_delete_btn = gr.Button(
                    "🗑️ Delete",
                    size="sm",
                    elem_classes=["image-action-btn", "btn-delete"]
                )

            # Hidden state to track selected gallery image index
            selected_gallery_index = gr.State(-1)

            # Close button at bottom
            with gr.Row():
                close_gallery_btn = gr.Button("✖️ Close Gallery", variant="secondary", size="lg")

        # ====================================================================
        # IMAGE PREVIEW SECTION
        # ====================================================================
        # Full-size image preview with metadata and actions (Gradio 5 compatible)

        with gr.Accordion("🖼️ Image Preview", open=False, visible=False, elem_classes=["image-preview-modal"]) as image_preview_modal:
            gr.Markdown("# 🖼️ Image Preview")

            preview_image = gr.Image(label="", type="pil", interactive=False)

            preview_metadata = gr.Markdown(value="", elem_classes=["image-metadata"])

            # Preview action buttons
            with gr.Row(elem_classes=["image-actions"]):
                preview_refine_btn = gr.Button(
                    "👁️ Open in Vision Chat",
                    size="lg",
                    variant="primary",
                    elem_classes=["image-action-btn", "btn-refine"]
                )
                preview_close_btn = gr.Button(
                    "✖️ Close",
                    size="lg",
                    variant="secondary"
                )

        # ====================================================================
        # THEME SETTINGS SECTION
        # ====================================================================
        # Theme customization panel (Gradio 5 compatible)

        with gr.Accordion("⚙️ Theme Settings", open=False, visible=False) as settings_modal:
            gr.Markdown("# ⚙️ Theme Settings")

            theme_components = create_theme_settings(theme_manager)

            # Extract components from dictionary
            theme_mode = theme_components["theme_mode"]
            color_scheme = theme_components["color_scheme"]
            layout_density = theme_components["layout_density"]
            theme_display = theme_components["theme_display"]
            apply_theme_btn = theme_components["apply_theme_btn"]
            reset_theme_btn = theme_components["reset_theme_btn"]

            close_settings_btn = gr.Button("✖️ Close", size="lg", variant="secondary")

        # ====================================================================
        # PROMPT COMPOSER SECTION
        # ====================================================================
        # Prompt building tool with tags and templates

        with gr.Accordion("🎨 Prompt Composer", open=False, visible=False) as composer_modal:
            gr.Markdown("# 🎨 Prompt Composer")

            composer_components = create_prompt_composer(prompt_composer)

            # Extract components from dictionary for easier access
            template_category_filter = composer_components["template_category_filter"]
            template_selector = composer_components["template_selector"]
            load_template_btn = composer_components["load_template_btn"]
            view_template_btn = composer_components["view_template_btn"]
            template_preview = composer_components["template_preview"]

            tag_buttons = composer_components["tag_buttons"]
            selected_tags_display = composer_components["selected_tags_display"]
            build_prompt_btn = composer_components["build_prompt_btn"]
            clear_tags_btn = composer_components["clear_tags_btn"]
            built_prompt = composer_components["built_prompt"]

            template_name_input = composer_components["template_name_input"]
            template_desc_input = composer_components["template_desc_input"]
            template_category_input = composer_components["template_category_input"]
            save_template_btn = composer_components["save_template_btn"]
            save_status = composer_components["save_status"]

            copy_to_prompt_btn = composer_components["copy_to_prompt_btn"]

            close_composer_btn = gr.Button("✖️ Close", size="lg", variant="secondary")

        # ====================================================================
        # EVENT HANDLERS
        # ====================================================================

        # Workflow helper functions
        def get_workflow_info_display():
            """Get formatted workflow info for display"""
            return _get_workflow_info_display(workflow_manager)

        def switch_workflow(workflow_name, category_filter):
            """Switch to selected workflow"""
            return _switch_workflow(workflow_name, category_filter, workflow_manager)

        def refresh_workflows(category_filter):
            """Refresh workflow list"""
            return _refresh_workflows(category_filter, workflow_manager)

        def filter_workflows_by_category(category):
            """Filter workflow dropdown by category"""
            return _filter_workflows_by_category(category, workflow_manager)

        def import_workflow_from_file(filepath):
            """Import workflow from uploaded file"""
            return _import_workflow_from_file(filepath, workflow_manager)

        def export_current_workflow():
            """Export current workflow"""
            return _export_current_workflow(workflow_manager)

        # Gallery helper functions
        def update_gallery_display(filter_text="", sort_by="newest", favorites_only=False):
            """Update gallery with filtering and sorting"""
            return _update_gallery_display(filter_text, sort_by, favorites_only, gallery)

        def show_gallery_stats():
            """Show gallery statistics"""
            return _show_gallery_stats(gallery)

        # Mode switching - unified handler for radio button
        def handle_mode_change(mode_choice):
            """Handle mode change from radio button with visual indicators and UI visibility"""
            return _handle_mode_change(mode_choice, mode_manager, vram_monitor)

        # Wire up mode radio button
        mode_radio.change(
            handle_mode_change,
            [mode_radio],
            [mode_status, smart_suggestion, mode_status_banner, mode_tip, idle_section, chat_section, generate_section, current_mode_state]
        )

        check_status_btn.click(
            lambda: (mode_manager._get_status_message(), gr.update(value="", visible=False)),
            None,
            [mode_status, smart_suggestion],
        )

        def get_enhanced_progress_html(message="Generating image...", estimated_time=None):
            """Create enhanced progress bar HTML"""
            return _get_enhanced_progress_html(message, estimated_time)

        # Chat functions
        def user_message(message, history):
            """Add user message to chat history"""
            return _user_message(message, history)

        def bot_message(history, model, current_prompt):
            """Process user message and generate bot response in text chat"""
            return _bot_message(
                history, model, current_prompt, mode_manager, vram_monitor,
                smart_switch, chat_with_ollama, show_toast, hide_toast
            )

        # Wire up chat
        msg.submit(user_message, [msg, chatbot], [msg, chatbot]).then(
            bot_message,
            [chatbot, model_dropdown, current_prompt_state],
            [chatbot, current_prompt_state, smart_suggestion, toast_notification, mode_status_banner, mode_tip, idle_section, chat_section, generate_section, current_mode_state],
        ).then(lambda x: x, [current_prompt_state], [prompt_display])

        send_btn.click(user_message, [msg, chatbot], [msg, chatbot]).then(
            bot_message,
            [chatbot, model_dropdown, current_prompt_state],
            [chatbot, current_prompt_state, smart_suggestion, toast_notification, mode_status_banner, mode_tip, idle_section, chat_section, generate_section, current_mode_state],
        ).then(lambda x: x, [current_prompt_state], [prompt_display])

        clear_chat_btn.click(lambda: ([], ""), None, [chatbot, current_prompt_state]).then(
            lambda: "", None, prompt_display
        )

        # Vision chat functions
        def vision_user_message(message, history):
            """Add user message to vision chat history"""
            return _vision_user_message(message, history)

        def vision_bot_message(history, current_image, current_prompt):
            """Process user message and generate bot response in vision chat"""
            return _vision_bot_message(history, current_image, current_prompt, vision_chat_with_ollama)

        # Wire up vision chat
        vision_msg.submit(
            vision_user_message, [vision_msg, vision_chatbot], [vision_msg, vision_chatbot]
        ).then(
            vision_bot_message,
            [vision_chatbot, current_image_state, current_prompt_state],
            [vision_chatbot, current_prompt_state],
        ).then(
            lambda x: x, [current_prompt_state], [prompt_display]
        )

        vision_send_btn.click(
            vision_user_message, [vision_msg, vision_chatbot], [vision_msg, vision_chatbot]
        ).then(
            vision_bot_message,
            [vision_chatbot, current_image_state, current_prompt_state],
            [vision_chatbot, current_prompt_state],
        ).then(
            lambda x: x, [current_prompt_state], [prompt_display]
        )

        clear_vision_btn.click(lambda: [], None, [vision_chatbot])

        # Update vision image preview when current image changes
        current_image_state.change(lambda x: x, [current_image_state], [vision_image_preview])

        # Prompt management
        prompt_display.change(lambda x: x, [prompt_display], [current_prompt_state])

        def extract_from_chat(history):
            """Extract prompt from chat history"""
            return _extract_from_chat(history, mode_manager, show_toast, hide_toast)

        extract_prompt_btn.click(extract_from_chat, [chatbot], [prompt_display, toast_notification])

        # Copy prompt to clipboard (via JS) with toast
        copy_prompt_btn.click(
            lambda x: x,
            [prompt_display],
            None,
            js="(prompt) => {navigator.clipboard.writeText(prompt); showToast('Prompt copied to clipboard!', 'success'); return prompt;}",
        )

        clear_prompt_btn.click(lambda: "", None, [prompt_display]).then(
            lambda: "", None, [current_prompt_state]
        )

        # Prompt History Handlers
        def load_selected_prompt(selected):
            """Load selected prompt from history"""
            return _load_selected_prompt(selected, prompt_history)

        def search_and_update_dropdown(query):
            """Search prompts and update dropdown"""
            return _search_and_update_dropdown(query, prompt_history)

        def refresh_history():
            """Refresh prompt history dropdown"""
            return _refresh_history(prompt_history)

        def export_history():
            """Export prompt history"""
            return _export_history(prompt_history)

        def import_history(filepath):
            """Import prompt history from file"""
            return _import_history(filepath, prompt_history)

        load_prompt_btn.click(load_selected_prompt, [prompt_history_dropdown], [prompt_display])

        search_btn.click(search_and_update_dropdown, [prompt_search], [prompt_history_dropdown])

        prompt_search.submit(search_and_update_dropdown, [prompt_search], [prompt_history_dropdown])

        refresh_history_btn.click(refresh_history, None, [prompt_history_dropdown])

        export_prompts_btn.click(export_history, None, [history_status, history_status])

        import_file.change(
            import_history, [import_file], [history_status, history_status, prompt_history_dropdown]
        )

        # Preset buttons
        def apply_preset(preset_name):
            """Apply generation preset"""
            return _apply_preset(preset_name)

        preset_fast.click(
            lambda: apply_preset("Fast Draft"), None, [width_slider, height_slider, steps_slider]
        )

        preset_balanced.click(
            lambda: apply_preset("Balanced"), None, [width_slider, height_slider, steps_slider]
        )

        preset_quality.click(
            lambda: apply_preset("High Quality"), None, [width_slider, height_slider, steps_slider]
        )

        preset_ultra.click(
            lambda: apply_preset("Ultra Detail"), None, [width_slider, height_slider, steps_slider]
        )

        # Update warnings when sliders change
        def update_warnings_from_sliders(steps, width, height):
            """Update VRAM warnings based on slider values"""
            return _update_warnings_from_sliders(steps, width, height, check_vram_warnings)

        steps_slider.change(
            update_warnings_from_sliders,
            [steps_slider, width_slider, height_slider],
            [vram_warning_display],
        )

        width_slider.change(
            update_warnings_from_sliders,
            [steps_slider, width_slider, height_slider],
            [vram_warning_display],
        )

        height_slider.change(
            update_warnings_from_sliders,
            [steps_slider, width_slider, height_slider],
            [vram_warning_display],
        )

        # Seed management functions
        def use_last_seed():
            """Use last seed from gallery"""
            return _use_last_seed(gallery)

        def adjust_seed(current_seed, adjustment):
            """Adjust seed by specified amount"""
            return _adjust_seed(current_seed, adjustment, gallery)

        def random_seed():
            """Generate random seed"""
            return _random_seed()

        def toggle_seed_lock(is_locked, current_seed):
            """Toggle seed lock"""
            return _toggle_seed_lock(is_locked, current_seed, seed_manager)

        def select_from_history(selected_seed):
            """Load seed from history"""
            return _select_from_history(selected_seed)

        def update_seed_history():
            """Update seed history dropdown"""
            return _update_seed_history(seed_manager)

        # Wire up seed management buttons
        use_last_seed_btn.click(use_last_seed, None, seed_input)

        seed_minus_100_btn.click(lambda s: adjust_seed(s, -100), [seed_input], seed_input)
        seed_minus_10_btn.click(lambda s: adjust_seed(s, -10), [seed_input], seed_input)
        seed_minus_1_btn.click(lambda s: adjust_seed(s, -1), [seed_input], seed_input)
        seed_plus_1_btn.click(lambda s: adjust_seed(s, 1), [seed_input], seed_input)
        seed_plus_10_btn.click(lambda s: adjust_seed(s, 10), [seed_input], seed_input)
        seed_plus_100_btn.click(lambda s: adjust_seed(s, 100), [seed_input], seed_input)
        seed_random_btn.click(random_seed, None, seed_input)

        # Seed lock toggle
        seed_lock_checkbox.change(
            toggle_seed_lock, [seed_lock_checkbox, seed_input], seed_lock_checkbox
        )

        # Seed history selection
        seed_history_dropdown.change(select_from_history, [seed_history_dropdown], seed_input)

        # Generation
        def generate_and_store(prompt_text, steps, width, height, seed_value, denoise, input_img):
            """Generate image and store in state and gallery"""
            return _generate_and_store(
                prompt_text, steps, width, height, seed_value, denoise, input_img,
                mode_manager, vram_monitor, session_stats, smart_switch, seed_manager,
                gallery, generate_image, get_enhanced_progress_html, show_toast, hide_toast
            )

        generate_btn.click(
            generate_and_store,
            [
                prompt_display,
                steps_slider,
                width_slider,
                height_slider,
                seed_input,
                denoise_slider,
                input_image,
            ],
            [
                generated_image,
                generation_status,
                current_image_state,
                session_gallery,
                gallery_info,
                stats_display,
                smart_suggestion,
                seed_history_dropdown,
                generation_progress,
                toast_notification,
                mode_status_banner,
                mode_tip,
                idle_section,
                chat_section,
                generate_section,
                current_mode_state,
            ],
        )

        # Quick Actions Toolbar (wired after generate_and_store is defined)
        quick_generate_btn.click(
            generate_and_store,
            [
                prompt_display,
                steps_slider,
                width_slider,
                height_slider,
                seed_input,
                denoise_slider,
                input_image,
            ],
            [
                generated_image,
                generation_status,
                current_image_state,
                session_gallery,
                gallery_info,
                stats_display,
                smart_suggestion,
                seed_history_dropdown,
                generation_progress,
                toast_notification,
                mode_status_banner,
                mode_tip,
                idle_section,
                chat_section,
                generate_section,
                current_mode_state,
            ],
        )

        quick_copy_btn.click(
            lambda x: x,
            [prompt_display],
            None,
            js="(prompt) => {navigator.clipboard.writeText(prompt); showToast('Prompt copied!', 'success'); return prompt;}",
        )

        quick_clear_btn.click(lambda: "", None, [prompt_display]).then(
            lambda: "", None, [current_prompt_state]
        )

        quick_extract_btn.click(extract_from_chat, [chatbot], [prompt_display, toast_notification])

        # Gallery click to load image into vision chat
        def load_gallery_image(evt: gr.SelectData):
            """Load clicked gallery image into vision chat, close modal, and switch to Vision Chat tab"""
            return _load_gallery_image(evt, gallery, mode_manager, show_toast, hide_toast)

        session_gallery.select(
            load_gallery_image,
            None,
            [
                current_image_state,
                gallery_info,
                vision_image_preview,
                mode_status,
                mode_radio,
                chat_tabs,
                toast_notification,
                gallery_modal,
                selected_gallery_index,
            ],
        )

        # Refresh models
        refresh_models_btn.click(
            lambda: gr.update(choices=get_available_models()), None, model_dropdown
        )

        # Keyboard shortcuts toggle
        shortcuts_state = gr.State(False)

        def toggle_shortcuts(current_state):
            """Toggle keyboard shortcuts help"""
            return _toggle_shortcuts(current_state)

        shortcuts_btn.click(toggle_shortcuts, [shortcuts_state], [shortcuts_state, shortcuts_help])

        # Gallery accordion handlers
        def open_gallery():
            """Open the gallery accordion"""
            return _open_gallery()

        def close_gallery():
            """Close the gallery accordion"""
            return _close_gallery()

        gallery_btn.click(open_gallery, None, gallery_modal)
        close_gallery_btn.click(close_gallery, None, gallery_modal)

        # Theme Settings accordion handlers
        def open_settings():
            """Open the theme settings accordion"""
            return _open_settings()

        def close_settings():
            """Close the theme settings accordion"""
            return _close_settings()

        def apply_theme(mode, scheme, density):
            """Apply theme settings"""
            return _apply_theme(mode, scheme, density, theme_manager)

        def reset_theme():
            """Reset theme to defaults"""
            return _reset_theme(theme_manager)

        settings_btn.click(open_settings, None, settings_modal)
        close_settings_btn.click(close_settings, None, settings_modal)

        apply_theme_btn.click(
            apply_theme,
            [theme_mode, color_scheme, layout_density],
            theme_display
        )

        reset_theme_btn.click(
            reset_theme,
            None,
            [theme_mode, color_scheme, layout_density, theme_display]
        )

        # Auto-switch toggle
        def toggle_auto_switch(enabled):
            """Toggle auto-switch functionality"""
            return _toggle_auto_switch(enabled, smart_switch)

        auto_switch_checkbox.change(toggle_auto_switch, [auto_switch_checkbox], None)

        # ====================================================================
        # PROMPT COMPOSER EVENT HANDLERS
        # ====================================================================

        # Open/close composer
        def open_composer():
            """Open the prompt composer accordion"""
            return _open_composer()

        def close_composer():
            """Close the prompt composer accordion"""
            return _close_composer()

        composer_btn.click(open_composer, None, composer_modal)
        close_composer_btn.click(close_composer, None, composer_modal)

        # Tag button clicks - universal handler
        def add_tag_to_composer(tag_name):
            """Add a tag to the composer"""
            return _add_tag_to_composer(tag_name, prompt_composer)

        # Wire up all tag buttons
        for tag_name, (btn, tag) in tag_buttons.items():
            btn.click(
                lambda tn=tag_name: add_tag_to_composer(tn),
                None,
                selected_tags_display
            )

        # Build prompt from tags
        def build_from_tags():
            """Build prompt from selected tags"""
            return _build_from_tags(prompt_composer)

        build_prompt_btn.click(build_from_tags, None, built_prompt)

        # Clear all tags
        def clear_all_tags():
            """Clear all selected tags"""
            return _clear_all_tags(prompt_composer)

        clear_tags_btn.click(clear_all_tags, None, [selected_tags_display, built_prompt])

        # Load template
        def load_template_handler(template_name):
            """Load a template"""
            return _load_template_handler(template_name, prompt_composer)

        load_template_btn.click(
            load_template_handler,
            [template_selector],
            [selected_tags_display, built_prompt]
        )

        # Copy built prompt to main prompt editor
        def copy_to_main_prompt(built):
            """Copy built prompt to main prompt editor"""
            return _copy_to_main_prompt(built)

        copy_to_prompt_btn.click(copy_to_main_prompt, [built_prompt], prompt_display)

        # Save custom template
        def save_custom_template(name, desc, category):
            """Save current composition as template"""
            return _save_custom_template(name, desc, category, prompt_composer)

        save_template_btn.click(
            save_custom_template,
            [template_name_input, template_desc_input, template_category_input],
            save_status
        )

        # ====================================================================
        # BATCH QUEUE EVENT HANDLERS
        # ====================================================================

        add_queue_btn.click(
            add_to_queue,
            [prompt_display, steps_slider, width_slider, height_slider, seed_input],
            [generation_status, queue_status],
        )

        batch_variations_btn.click(
            lambda p, st, w, h, s, count: add_batch_variations(p, st, w, h, s, int(count)),
            [
                prompt_display,
                steps_slider,
                width_slider,
                height_slider,
                seed_input,
                variation_count,
            ],
            [generation_status, queue_status],
        )

        process_queue_btn.click(
            process_queue, None, [generated_image, generation_status, queue_status, stats_display]
        ).then(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        clear_completed_btn.click(clear_queue, None, queue_status)

        cancel_all_btn.click(cancel_all_queue, None, queue_status)

        # ====================================================================
        # ENHANCED GALLERY EVENT HANDLERS
        # ====================================================================

        refresh_gallery_btn.click(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        gallery_stats_btn.click(show_gallery_stats, None, gallery_info)

        # Auto-refresh gallery when filter/sort changes
        gallery_filter.change(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        gallery_sort.change(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        favorites_only_check.change(
            update_gallery_display,
            [gallery_filter, gallery_sort, favorites_only_check],
            [session_gallery, gallery_info],
        )

        # ====================================================================
        # IMAGE ACTION BUTTONS EVENT HANDLERS
        # ====================================================================

        # Generated image action buttons
        def start_seed_variations(prompt, steps, width, height):
            """Generate 4 seed variations of current image"""
            return _start_seed_variations(prompt, steps, width, height, gallery, gen_queue, show_toast)

        def refine_in_vision(image):
            """Load current image into Vision Chat"""
            return _refine_in_vision(image, mode_manager, vram_monitor, gallery, show_toast)

        def toggle_favorite_generated():
            """Toggle favorite status of last generated image"""
            return _toggle_favorite_generated(gallery, show_toast)

        def copy_seed_to_clipboard():
            """Copy current seed to clipboard"""
            return _copy_seed_to_clipboard(seed_manager, show_toast)

        # Wire up generated image action buttons
        gen_variations_btn.click(
            start_seed_variations,
            [prompt_display, steps_slider, width_slider, height_slider],
            [toast_notification, queue_status],
        )

        gen_refine_btn.click(
            refine_in_vision,
            [generated_image],
            [vision_image_preview, gallery_info, mode_radio, mode_status, chat_tabs, toast_notification, mode_status_banner, mode_tip],
        )

        gen_favorite_btn.click(toggle_favorite_generated, None, toast_notification)

        gen_copy_seed_btn.click(
            copy_seed_to_clipboard,
            None,
            toast_notification,
            js="(seed) => {const s = String(seed || ''); navigator.clipboard.writeText(s); return s;}"
        )

        # Image preview modal handlers
        def open_image_preview(image):
            """Open full-size preview of generated image"""
            return _open_image_preview(image, gallery)

        def close_image_preview():
            """Close image preview accordion"""
            return _close_image_preview()

        # Click on generated image opens preview
        generated_image.select(
            open_image_preview,
            [generated_image],
            [image_preview_modal, preview_image, preview_metadata],
        )

        preview_close_btn.click(close_image_preview, None, image_preview_modal)

        # Refine from preview modal
        preview_refine_btn.click(
            refine_in_vision,
            [preview_image],
            [vision_image_preview, gallery_info, mode_radio, mode_status, chat_tabs, toast_notification, mode_status_banner, mode_tip],
        ).then(
            close_image_preview,
            None,
            image_preview_modal,
        )

        # Gallery action button handlers
        def gallery_toggle_favorite(index):
            """Toggle favorite status of selected gallery image"""
            return _gallery_toggle_favorite(index, gallery, show_toast, update_gallery_display)

        def gallery_use_img2img(index):
            """Load selected gallery image into img2img input"""
            return _gallery_use_img2img(index, gallery, show_toast)

        def gallery_open_vision(index):
            """Load selected gallery image into Vision Chat"""
            return _gallery_open_vision(index, gallery, mode_manager, vram_monitor, show_toast)

        def gallery_delete_image(index):
            """Delete selected gallery image"""
            return _gallery_delete_image(index, gallery, show_toast, update_gallery_display)

        # Wire up gallery action buttons
        gallery_favorite_btn.click(
            gallery_toggle_favorite,
            [selected_gallery_index],
            [toast_notification, session_gallery, gallery_info],
        )

        gallery_img2img_btn.click(
            gallery_use_img2img,
            [selected_gallery_index],
            [toast_notification, input_image],
        )

        gallery_vision_btn.click(
            gallery_open_vision,
            [selected_gallery_index],
            [toast_notification, vision_image_preview, mode_radio, mode_status, chat_tabs, gallery_modal, mode_status_banner, mode_tip],
        )

        gallery_delete_btn.click(
            gallery_delete_image,
            [selected_gallery_index],
            [toast_notification, session_gallery, gallery_info],
        )

        # ====================================================================
        # WORKFLOW MANAGER EVENT HANDLERS (Phase 3)
        # ====================================================================

        # Initialize workflow info on load
        app.load(get_workflow_info_display, None, workflow_info)

        # Workflow selection
        workflow_dropdown.change(
            switch_workflow,
            [workflow_dropdown, workflow_category_filter],
            [workflow_dropdown, workflow_info, generation_status],
        )

        # Refresh workflows
        workflow_refresh_btn.click(
            refresh_workflows,
            [workflow_category_filter],
            [workflow_dropdown, workflow_info, generation_status],
        )

        # Category filter
        workflow_category_filter.change(
            filter_workflows_by_category, [workflow_category_filter], workflow_dropdown
        )

        # Import workflow
        workflow_import_btn.click(
            import_workflow_from_file,
            [workflow_upload_file],
            [workflow_info, generation_status, workflow_dropdown],
        )

        # Export workflow
        workflow_export_btn.click(export_current_workflow, None, generation_status)

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("AI IMAGE CHAT - Phase 2 (Vision Chat)")
    logger.info("=" * 60)
    logger.info("User: ant")
    logger.info("Hostname: nobara-laptop")
    logger.info(f"ComfyUI: {COMFYUI_API}")
    logger.info(f"Ollama: {OLLAMA_API}")
    logger.info(f"Text Chat Model: {OLLAMA_CHAT_MODEL}")
    logger.info(f"Vision Chat Model: {OLLAMA_VISION_MODEL}")
    logger.info(f"FLUX Finetune: {FINETUNE_NAME}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Access URLs:")
    logger.info("• Laptop: http://localhost:7860")
    logger.info("• Desktop: http://192.168.1.175:7860")
    logger.info("")
    logger.info("Workflow:")
    logger.info("1. Text Chat → Develop prompts")
    logger.info("2. Generate → Create images")
    logger.info("3. Vision Chat → AI sees image & suggests refinements")
    logger.info("4. Generate → Create refined images")
    logger.info("")
    logger.info("=" * 60)

    app = create_app()
    app.launch(server_name=GRADIO_SERVER_NAME, server_port=GRADIO_SERVER_PORT, share=GRADIO_SHARE)
