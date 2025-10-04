"""
Event handlers package.

This package contains all event handler functions extracted from app.py,
organized by functionality into separate modules.
"""

# Mode handlers (2 functions)
from .mode_handlers import (
    handle_mode_change,
    toggle_auto_switch,
)

# Gallery handlers (9 functions)
from .gallery_handlers import (
    update_gallery_display,
    show_gallery_stats,
    load_gallery_image,
    open_gallery,
    close_gallery,
    gallery_toggle_favorite,
    gallery_use_img2img,
    gallery_open_vision,
    gallery_delete_image,
)

# Workflow handlers (6 functions)
from .workflow_handlers import (
    get_workflow_info_display,
    switch_workflow,
    refresh_workflows,
    filter_workflows_by_category,
    import_workflow_from_file,
    export_current_workflow,
)

# Chat handlers (10 functions)
from .chat_handlers import (
    user_message,
    bot_message,
    vision_user_message,
    vision_bot_message,
    extract_from_chat,
    load_selected_prompt,
    search_and_update_dropdown,
    refresh_history,
    export_history,
    import_history,
)

# Generation handlers (13 functions)
from .generation_handlers import (
    apply_preset,
    update_warnings_from_sliders,
    use_last_seed,
    adjust_seed,
    random_seed,
    toggle_seed_lock,
    select_from_history,
    update_seed_history,
    generate_and_store,
    start_seed_variations,
    refine_in_vision,
    toggle_favorite_generated,
    copy_seed_to_clipboard,
)

# UI handlers (18 functions)
from .ui_handlers import (
    show_toast,
    hide_toast,
    get_enhanced_progress_html,
    toggle_shortcuts,
    open_settings,
    close_settings,
    apply_theme,
    reset_theme,
    open_composer,
    close_composer,
    add_tag_to_composer,
    build_from_tags,
    clear_all_tags,
    load_template_handler,
    copy_to_main_prompt,
    save_custom_template,
    open_image_preview,
    close_image_preview,
)

__all__ = [
    # Mode handlers (2)
    "handle_mode_change",
    "toggle_auto_switch",
    # Gallery handlers (9)
    "update_gallery_display",
    "show_gallery_stats",
    "load_gallery_image",
    "open_gallery",
    "close_gallery",
    "gallery_toggle_favorite",
    "gallery_use_img2img",
    "gallery_open_vision",
    "gallery_delete_image",
    # Workflow handlers (6)
    "get_workflow_info_display",
    "switch_workflow",
    "refresh_workflows",
    "filter_workflows_by_category",
    "import_workflow_from_file",
    "export_current_workflow",
    # Chat handlers (10)
    "user_message",
    "bot_message",
    "vision_user_message",
    "vision_bot_message",
    "extract_from_chat",
    "load_selected_prompt",
    "search_and_update_dropdown",
    "refresh_history",
    "export_history",
    "import_history",
    # Generation handlers (13)
    "apply_preset",
    "update_warnings_from_sliders",
    "use_last_seed",
    "adjust_seed",
    "random_seed",
    "toggle_seed_lock",
    "select_from_history",
    "update_seed_history",
    "generate_and_store",
    "start_seed_variations",
    "refine_in_vision",
    "toggle_favorite_generated",
    "copy_seed_to_clipboard",
    # UI handlers (18)
    "show_toast",
    "hide_toast",
    "get_enhanced_progress_html",
    "toggle_shortcuts",
    "open_settings",
    "close_settings",
    "apply_theme",
    "reset_theme",
    "open_composer",
    "close_composer",
    "add_tag_to_composer",
    "build_from_tags",
    "clear_all_tags",
    "load_template_handler",
    "copy_to_main_prompt",
    "save_custom_template",
    "open_image_preview",
    "close_image_preview",
]
