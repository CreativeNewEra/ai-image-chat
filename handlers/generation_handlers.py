"""
Image generation event handlers.

This module contains event handlers for image generation, presets, seed management,
and image action buttons.
"""

import logging
import random

import gradio as gr

from core import Mode
from config import OLLAMA_VISION_MODEL, PRESETS

logger = logging.getLogger(__name__)


def apply_preset(preset_name):
    """
    Apply generation preset.

    Args:
        preset_name: Name of preset to apply

    Returns:
        tuple: (width, height, steps)
    """
    preset = PRESETS.get(preset_name, PRESETS["Balanced"])
    return preset["width"], preset["height"], preset["steps"]


def update_warnings_from_sliders(steps, width, height, check_vram_warnings_func):
    """
    Update VRAM warnings when sliders change.

    Args:
        steps: Number of generation steps
        width: Image width
        height: Image height
        check_vram_warnings_func: Function to check VRAM warnings

    Returns:
        gr.update: Warning display update
    """
    warning_text, warning_visible = check_vram_warnings_func(steps, width, height)
    return gr.update(value=warning_text, visible=warning_visible)


def use_last_seed(gallery):
    """
    Use the last generated seed.

    Args:
        gallery: ImageGallery instance

    Returns:
        str: Last seed value as string, or empty string
    """
    last = gallery.get_last_seed()
    if last is not None:
        return str(last)
    return ""


def adjust_seed(current_seed, adjustment, gallery):
    """
    Adjust seed by specified amount.

    Args:
        current_seed: Current seed value as string
        adjustment: Amount to adjust by (positive or negative)
        gallery: ImageGallery instance

    Returns:
        str: Adjusted seed value as string
    """
    try:
        if current_seed and current_seed.strip():
            seed_val = int(current_seed)
        else:
            seed_val = gallery.get_last_seed()
            if seed_val is None:
                seed_val = random.randint(0, 2**32 - 1)

        new_seed = max(0, seed_val + adjustment)
        return str(new_seed)
    except:
        return current_seed


def random_seed():
    """
    Generate random seed.

    Returns:
        str: Random seed value as string
    """
    return str(random.randint(0, 2**32 - 1))


def toggle_seed_lock(is_locked, current_seed, seed_manager):
    """
    Toggle seed lock.

    Args:
        is_locked: Boolean indicating if seed should be locked
        current_seed: Current seed value as string
        seed_manager: SeedManager instance

    Returns:
        bool: The locked state
    """
    if is_locked:
        # Lock the seed
        try:
            seed_val = int(current_seed) if current_seed else None
            if seed_val is not None:
                seed_manager.lock_seed(seed_val)
            return is_locked
        except:
            return False
    else:
        # Unlock the seed
        seed_manager.unlock_seed()
        return is_locked


def select_from_history(selected_seed):
    """
    Load seed from history.

    Args:
        selected_seed: Selected seed value

    Returns:
        str: Seed value as string, or empty string
    """
    if selected_seed:
        return str(selected_seed)
    return ""


def update_seed_history(seed_manager):
    """
    Update seed history dropdown.

    Args:
        seed_manager: SeedManager instance

    Returns:
        gr.update: Dropdown update with seed history
    """
    history = seed_manager.get_history()
    return gr.update(choices=history)


def generate_and_store(
    prompt_text,
    steps,
    width,
    height,
    seed_value,
    denoise,
    input_img,
    mode_manager,
    vram_monitor,
    session_stats,
    smart_switch,
    seed_manager,
    gallery,
    generate_image_func,
    get_enhanced_progress_html_func,
    show_toast_func,
    hide_toast_func
):
    """
    Generate image and store in state and gallery.

    Args:
        prompt_text: The prompt text
        steps: Number of generation steps
        width: Image width
        height: Image height
        seed_value: Seed value as string
        denoise: Denoise strength (0.0-1.0)
        input_img: Input image for img2img (None for text2img)
        mode_manager: ModeManager instance
        vram_monitor: VRAMMonitor instance
        session_stats: SessionStats instance
        smart_switch: SmartSwitchManager instance
        seed_manager: SeedManager instance
        gallery: ImageGallery instance
        generate_image_func: Function to generate images
        get_enhanced_progress_html_func: Function to create progress HTML
        show_toast_func: Function to show toast notifications
        hide_toast_func: Function to hide toast notifications

    Yields:
        tuple: Progress and result updates for UI components
    """
    # Auto-switch to GENERATE mode if needed
    toast_update = hide_toast_func()
    banner_update = gr.update()
    tip_update = gr.update()
    idle_vis = gr.update()
    chat_vis = gr.update()
    generate_vis = gr.update()
    mode_state = gr.update()

    if mode_manager.get_mode() != Mode.GENERATE:
        mode_manager.switch_to_generate()
        vram = vram_monitor.get_vram_usage()
        vram_text = f"{vram['used_gb']} GB" if vram['available'] else "N/A"

        toast_update = show_toast_func("🟠 Switching to Generate Mode...", "warning")
        banner_update = gr.update(
            value=f"🟠 **GENERATE MODE** ({vram_text} VRAM)",
            elem_classes=["mode-status-banner", "mode-generate"]
        )
        tip_update = gr.update(
            value="💡 **Tip:** Click generated images in Gallery to refine them with Vision Chat",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-generate"]
        )
        # Update UI visibility
        idle_vis = gr.update(visible=False)
        chat_vis = gr.update(visible=False)
        generate_vis = gr.update(visible=True)
        mode_state = "GENERATE"

    # Show enhanced progress bar with estimated time
    stats = session_stats.get_stats()
    avg_time = stats.get("avg_time", 0)
    estimated_time = round(avg_time) if avg_time > 0 else None
    progress_html = get_enhanced_progress_html_func(
        message="🎨 Generating image...",
        estimated_time=estimated_time
    )

    yield (
        None,  # image
        "🎨 Generating image...",  # status
        None,  # current_image_state
        gr.update(),  # gallery
        gr.update(),  # gallery_info
        gr.update(),  # stats
        gr.update(value="", visible=False),  # smart_suggestion
        gr.update(),  # seed_history
        gr.update(value=progress_html, visible=True),  # progress
        toast_update,  # toast_notification
        banner_update,  # mode_status_banner
        tip_update,  # mode_tip
        idle_vis,  # idle_section
        chat_vis,  # chat_section
        generate_vis,  # generate_section
        mode_state,  # current_mode_state
    )

    image, status, actual_seed, stats = generate_image_func(
        prompt_text,
        steps,
        width,
        height,
        seed_value,
        denoise=denoise,
        input_image_path=input_img,
    )

    # Update gallery display
    gallery_images = gallery.get_images()
    gallery_count = len(gallery_images)
    info = (
        f"Generated {gallery_count} image{'s' if gallery_count != 1 else ''} this session"
    )

    if actual_seed is not None:
        info += f" | Last seed: {actual_seed}"

    # Check for smart switch suggestion
    suggestion_update = gr.update(value="", visible=False)
    if image is not None:
        suggested = smart_switch.should_suggest_switch(
            "image_generated", mode_manager.get_mode()
        )
        if suggested:
            suggestion_msg = smart_switch.get_suggestion_message(suggested)
            suggestion_update = gr.update(value=suggestion_msg, visible=True)

    # Update seed history dropdown
    seed_history_update = gr.update(choices=seed_manager.get_history())

    # Hide progress bar and toast
    progress_update = gr.update(value="", visible=False)
    final_toast = hide_toast_func()

    yield image, status, image, gallery_images, info, stats, suggestion_update, seed_history_update, progress_update, final_toast, banner_update, tip_update, idle_vis, chat_vis, generate_vis, mode_state


def start_seed_variations(prompt, steps, width, height, gallery, gen_queue, show_toast_func):
    """
    Generate 4 seed variations of current image.

    Args:
        prompt: Prompt text
        steps: Number of generation steps
        width: Image width
        height: Image height
        gallery: ImageGallery instance
        gen_queue: GenerationQueue instance
        show_toast_func: Function to show toast notifications

    Returns:
        tuple: (toast_update, queue_status)
    """
    current_seed = gallery.get_last_seed()
    if current_seed is None:
        return show_toast_func("⚠️ No seed available for variations", "error"), gr.update()

    # Get current prompt
    current_prompt = prompt or "No prompt"

    # Add 4 variations to queue
    gen_queue.add_job(
        prompt=current_prompt,
        seed=current_seed + 1,
        steps=steps,
        width=width,
        height=height
    )
    gen_queue.add_job(
        prompt=current_prompt,
        seed=current_seed + 10,
        steps=steps,
        width=width,
        height=height
    )
    gen_queue.add_job(
        prompt=current_prompt,
        seed=current_seed + 100,
        steps=steps,
        width=width,
        height=height
    )
    gen_queue.add_job(
        prompt=current_prompt,
        seed=current_seed + 1000,
        steps=steps,
        width=width,
        height=height
    )

    toast_msg = show_toast_func(f"✅ Added 4 seed variations to queue (base: {current_seed})", "success")
    queue_msg = gen_queue.get_status()
    return toast_msg, queue_msg


def refine_in_vision(image, mode_manager, vram_monitor, gallery, show_toast_func):
    """
    Load current image into Vision Chat.

    Args:
        image: Image to refine
        mode_manager: ModeManager instance
        vram_monitor: VRAMMonitor instance
        gallery: ImageGallery instance
        show_toast_func: Function to show toast notifications

    Returns:
        tuple: (vision_image_preview, gallery_info, mode_radio, mode_status,
                tab_update, toast, banner_update, tip_update)
    """
    if image is None:
        return (
            gr.update(),  # vision_image_preview
            gr.update(),  # gallery_info
            gr.update(),  # mode_radio
            gr.update(),  # mode_status
            gr.update(),  # chat_tabs
            show_toast_func("⚠️ No image to refine", "error"),  # toast
            gr.update(),  # mode_status_banner
            gr.update(),  # mode_tip
        )

    # Switch to Chat mode and Vision Chat tab if needed
    mode_status_msg = mode_manager._get_status_message()
    mode_radio_value = "💬 Chat"
    tab_update = gr.update(selected=1)  # Vision Chat tab
    toast_update = show_toast_func("👁️ Opening in Vision Chat...", "success")

    # Get VRAM info
    vram = vram_monitor.get_vram_usage()
    vram_text = f"{vram['used_gb']} GB" if vram['available'] else "N/A"

    if mode_manager.get_mode() != Mode.CHAT:
        mode_manager.switch_to_chat(preload_model=OLLAMA_VISION_MODEL)
        mode_status_msg = mode_manager._get_status_message()
        banner_update = gr.update(
            value=f"🟢 **CHAT MODE** ({vram_text} VRAM)",
            elem_classes=["mode-status-banner", "mode-chat"]
        )
        tip_update = gr.update(
            value="💡 **Tip:** Use Vision Chat to refine this image with AI guidance",
            visible=True,
            elem_classes=["mode-tip", "mode-tip-chat"]
        )
    else:
        banner_update = gr.update()
        tip_update = gr.update()

    # Get image info for gallery
    if len(gallery.images) > 0:
        last_image = gallery.images[-1]
        info_text = f"Loaded into Vision Chat: {last_image.get('prompt', 'Unknown')[:50]}..."
    else:
        info_text = "Image loaded"

    return (
        image,  # vision_image_preview
        info_text,  # gallery_info
        mode_radio_value,  # mode_radio
        mode_status_msg,  # mode_status
        tab_update,  # chat_tabs
        toast_update,  # toast
        banner_update,  # mode_status_banner
        tip_update,  # mode_tip
    )


def toggle_favorite_generated(gallery, show_toast_func):
    """
    Toggle favorite status of last generated image.

    Args:
        gallery: ImageGallery instance
        show_toast_func: Function to show toast notifications

    Returns:
        gr.update: Toast update
    """
    last_meta = gallery.get_last_image_metadata()
    if not last_meta:
        return show_toast_func("⚠️ No image to favorite", "error")

    # Get the last image path
    images = gallery.get_images()
    if not images:
        return show_toast_func("⚠️ No images in gallery", "error")

    last_image_path = images[0][0]  # First image (newest) path
    is_fav = gallery.toggle_favorite(last_image_path)

    icon = "⭐" if is_fav else "☆"
    status = "added to" if is_fav else "removed from"
    return show_toast_func(f"{icon} Image {status} favorites", "success")


def copy_seed_to_clipboard(seed_manager, show_toast_func):
    """
    Copy current seed to clipboard.

    Args:
        seed_manager: SeedManager instance
        show_toast_func: Function to show toast notifications

    Returns:
        gr.update: Toast update
    """
    current_seed = seed_manager.get_last_seed()
    if current_seed is None:
        return show_toast_func("⚠️ No seed available", "error")
    return show_toast_func(f"📋 Seed {current_seed} copied!", "success")
