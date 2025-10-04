"""
Gallery event handlers.

This module contains event handlers for gallery operations including
filtering, sorting, favorites, and image actions.
"""

import logging

import gradio as gr

from core import Mode
from config import OLLAMA_VISION_MODEL

logger = logging.getLogger(__name__)


def update_gallery_display(filter_text, sort_by, favorites_only, gallery):
    """
    Update gallery with filtering and sorting.

    Args:
        filter_text: Text filter for prompts
        sort_by: Sort order ("newest", "oldest", "seed", "resolution")
        favorites_only: Show only favorited images
        gallery: ImageGallery instance

    Returns:
        tuple: (images, info)
    """
    images = gallery.get_images(filter_text, sort_by, favorites_only)
    total = len(gallery.images)
    shown = len(images)

    if favorites_only:
        info = f"Showing {shown} favorite images (out of {total} total)"
    elif filter_text:
        info = f"Showing {shown} images matching '{filter_text}' (out of {total} total)"
    else:
        info = f"Showing all {shown} images"

    return images, info


def show_gallery_stats(gallery):
    """
    Show gallery statistics.

    Args:
        gallery: ImageGallery instance

    Returns:
        str: Formatted statistics string
    """
    stats = gallery.get_gallery_stats()
    if stats["total"] == 0:
        return "No images in gallery"

    return f"📊 Gallery Stats\n\nTotal Images: {stats['total']}\n⭐ Favorites: {stats['favorites']}\n💾 Total Size: {stats['total_size_mb']} MB"


def load_gallery_image(evt, gallery, mode_manager, show_toast_func, hide_toast_func):
    """
    Load clicked gallery image into vision chat, close modal, and switch to Vision Chat tab.

    Args:
        evt: SelectData event from gallery click
        gallery: ImageGallery instance
        mode_manager: ModeManager instance
        show_toast_func: Function to show toast notifications
        hide_toast_func: Function to hide toast notifications

    Returns:
        tuple: (current_image_state, gallery_info, vision_image_preview, mode_status,
                mode_radio, tab_update, toast_notification, modal_update, selected_gallery_index)
    """
    index = evt.index
    img_data = gallery.get_image_by_index(index)

    if img_data:
        image = img_data["image"]
        prompt = img_data["prompt"]
        seed = img_data["seed"]
        settings = img_data["settings"]

        info_text = f"Loaded image from gallery\nPrompt: {prompt[:100]}...\nSeed: {seed}\nSettings: {settings['width']}x{settings['height']}, {settings['steps']} steps"

        # Auto-switch to Chat mode if needed
        mode_status_msg = ""  # Will be set from mode_manager
        mode_radio_value = "💬 Chat"
        toast_update = hide_toast_func()

        if mode_manager.get_mode() != Mode.CHAT:
            mode_manager.switch_to_chat(preload_model=OLLAMA_VISION_MODEL)
            mode_status_msg = mode_manager._get_status_message()
            mode_radio_value = "💬 Chat"
            toast_update = show_toast_func("✅ Image loaded - Vision Chat ready!", "success")

        # Switch to Vision Chat tab (index 1 = second tab)
        tab_update = gr.update(selected=1)

        # Close the gallery accordion
        modal_update = gr.update(visible=False, open=False)

        return (
            image,  # current_image_state
            info_text,  # gallery_info
            image,  # vision_image_preview
            mode_status_msg,  # mode_status
            mode_radio_value,  # mode_radio
            tab_update,  # chat_tabs
            toast_update,  # toast_notification
            modal_update,  # gallery_modal
            index,  # selected_gallery_index
        )

    return None, "Failed to load image", None, gr.update(), gr.update(), gr.update(), hide_toast_func(), gr.update(), -1


def open_gallery():
    """
    Open the gallery accordion.

    Returns:
        gr.update: Update to show and open gallery modal
    """
    return gr.update(visible=True, open=True)


def close_gallery():
    """
    Close the gallery accordion.

    Returns:
        gr.update: Update to hide and close gallery modal
    """
    return gr.update(visible=False, open=False)


def gallery_toggle_favorite(index, gallery, show_toast_func):
    """
    Toggle favorite status of selected gallery image.

    Args:
        index: Image index in gallery
        gallery: ImageGallery instance
        show_toast_func: Function to show toast notifications

    Returns:
        tuple: (toast_update, gallery_images, info)
    """
    if index < 0:
        return show_toast_func("⚠️ Please select an image first", "error"), gr.update(), gr.update()

    images = gallery.get_images()
    if index >= len(images):
        return show_toast_func("⚠️ Image not found", "error"), gr.update(), gr.update()

    image_path = images[index][0]  # Get path from tuple
    is_fav = gallery.toggle_favorite(image_path)

    # Update gallery display
    gallery_images, info = update_gallery_display("", "newest", False, gallery)

    icon = "⭐" if is_fav else "☆"
    status = "added to" if is_fav else "removed from"
    return show_toast_func(f"{icon} Image {status} favorites", "success"), gallery_images, info


def gallery_use_img2img(index, gallery, show_toast_func):
    """
    Load selected gallery image into img2img input.

    Args:
        index: Image index in gallery
        gallery: ImageGallery instance
        show_toast_func: Function to show toast notifications

    Returns:
        tuple: (toast_update, image)
    """
    if index < 0:
        return show_toast_func("⚠️ Please select an image first", "error"), gr.update()

    img_data = gallery.get_image_by_index(index)
    if not img_data:
        return show_toast_func("⚠️ Image not found", "error"), gr.update()

    return show_toast_func("🎨 Image loaded for img2img", "success"), img_data["image"]


def gallery_open_vision(index, gallery, mode_manager, vram_monitor, show_toast_func):
    """
    Load selected gallery image into Vision Chat.

    Args:
        index: Image index in gallery
        gallery: ImageGallery instance
        mode_manager: ModeManager instance
        vram_monitor: VRAMMonitor instance
        show_toast_func: Function to show toast notifications

    Returns:
        tuple: (toast_update, vision_image_preview, mode_radio, mode_status, tab_update,
                modal_update, banner_update, tip_update)
    """
    if index < 0:
        return (
            show_toast_func("⚠️ Please select an image first", "error"),
            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        )

    img_data = gallery.get_image_by_index(index)
    if not img_data:
        return (
            show_toast_func("⚠️ Image not found", "error"),
            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        )

    # Switch to Chat mode and Vision Chat tab if needed
    mode_status_msg = mode_manager._get_status_message()
    mode_radio_value = "💬 Chat"
    tab_update = gr.update(selected=1)
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

    # Close gallery accordion
    modal_update = gr.update(visible=False, open=False)

    return (
        toast_update,  # toast
        img_data["image"],  # vision_image_preview
        mode_radio_value,  # mode_radio
        mode_status_msg,  # mode_status
        tab_update,  # chat_tabs
        modal_update,  # gallery_modal
        banner_update,  # mode_status_banner
        tip_update,  # mode_tip
    )


def gallery_delete_image(index, gallery, show_toast_func):
    """
    Delete selected gallery image.

    Args:
        index: Image index in gallery
        gallery: ImageGallery instance
        show_toast_func: Function to show toast notifications

    Returns:
        tuple: (toast_update, gallery_images, info)
    """
    if index < 0:
        return show_toast_func("⚠️ Please select an image first", "error"), gr.update(), gr.update()

    images = gallery.get_images()
    if index >= len(images):
        return show_toast_func("⚠️ Image not found", "error"), gr.update(), gr.update()

    image_path = images[index][0]
    gallery.delete_image(image_path)

    # Update gallery display
    gallery_images, info = update_gallery_display("", "newest", False, gallery)

    return show_toast_func("🗑️ Image deleted", "success"), gallery_images, info
