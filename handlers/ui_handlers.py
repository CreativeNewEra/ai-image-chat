"""
UI interaction event handlers.

This module contains event handlers for UI interactions including toast notifications,
theme settings, prompt composer, keyboard shortcuts, and image preview modal.
"""

import logging

import gradio as gr

logger = logging.getLogger(__name__)


def show_toast(message, toast_type="info"):
    """
    Show a toast notification (returns update for toast component).

    Args:
        message: Toast message text
        toast_type: Type of toast ("info", "success", "warning", "error")

    Returns:
        gr.update: Toast component update
    """
    toast_class = f"toast toast-{toast_type}"
    return gr.update(value=f"**{message}**", visible=True, elem_classes=[toast_class])


def hide_toast():
    """
    Hide toast notification.

    Returns:
        gr.update: Toast component update to hide
    """
    return gr.update(value="", visible=False)


def get_enhanced_progress_html(message="Generating image...", estimated_time=None):
    """
    Create enhanced progress bar HTML with animation and estimated time.

    Args:
        message: Progress message text
        estimated_time: Estimated time remaining in seconds (optional)

    Returns:
        str: HTML for progress bar
    """
    time_display = ""
    if estimated_time:
        time_display = f'<div class="progress-time">~{estimated_time}s remaining</div>'

    return f"""
    <div class="generation-progress-enhanced">
        <div class="progress-info">
            <span class="progress-label">{message}</span>
            {time_display}
        </div>
        <div class="progress-container">
            <div class="progress-bar animated" style="width: 100%;"></div>
        </div>
    </div>
    """


def toggle_shortcuts(current_state):
    """
    Toggle keyboard shortcuts help.

    Args:
        current_state: Current shortcuts visibility state

    Returns:
        tuple: (new_state, accordion_update)
    """
    return not current_state, gr.update(visible=not current_state, open=not current_state)


def open_settings():
    """
    Open the theme settings accordion.

    Returns:
        gr.update: Accordion update to show and open
    """
    return gr.update(visible=True, open=True)


def close_settings():
    """
    Close the theme settings accordion.

    Returns:
        gr.update: Accordion update to hide and close
    """
    return gr.update(visible=False, open=False)


def apply_theme(mode, scheme, density, theme_manager):
    """
    Apply theme settings.

    Args:
        mode: Theme mode ("Auto", "Light", "Dark")
        scheme: Color scheme name
        density: Layout density ("Compact", "Default", "Spacious")
        theme_manager: ThemeManager instance

    Returns:
        str: Theme display string
    """
    # Map color scheme display name to ID
    scheme_map = {info["name"]: key for key, info in theme_manager.COLOR_SCHEMES.items()}
    scheme_id = scheme_map.get(scheme, "default")

    theme_manager.set_mode(mode)
    theme_manager.set_color_scheme(scheme_id)
    theme_manager.set_layout_density(density)

    gr.Info(f"✨ Theme applied: {scheme} ({mode} mode, {density} density)")
    return theme_manager.get_theme_display()


def reset_theme(theme_manager):
    """
    Reset theme to defaults.

    Args:
        theme_manager: ThemeManager instance

    Returns:
        tuple: (mode, scheme, density, theme_display)
    """
    theme_manager.reset_to_defaults()
    gr.Info("🔄 Theme reset to defaults")
    return (
        theme_manager.get_mode(),
        theme_manager.COLOR_SCHEMES[theme_manager.get_color_scheme()]["name"],
        theme_manager.get_layout_density(),
        theme_manager.get_theme_display(),
    )


def open_composer():
    """
    Open the prompt composer accordion.

    Returns:
        gr.update: Accordion update to show and open
    """
    return gr.update(visible=True, open=True)


def close_composer():
    """
    Close the prompt composer accordion.

    Returns:
        gr.update: Accordion update to hide and close
    """
    return gr.update(visible=False, open=False)


def add_tag_to_composer(tag_name, prompt_composer):
    """
    Add a tag to the composer.

    Args:
        tag_name: Name of tag to add
        prompt_composer: PromptComposer instance

    Returns:
        str: Updated selected tags display
    """
    # Find the tag object
    for category_tags in prompt_composer.TAG_LIBRARY.values():
        for tag in category_tags:
            if tag.name == tag_name:
                prompt_composer.add_tag(tag)
                break
    return prompt_composer.get_selected_tags_display()


def build_from_tags(prompt_composer):
    """
    Build prompt from selected tags.

    Args:
        prompt_composer: PromptComposer instance

    Returns:
        str: Built prompt text
    """
    prompt = prompt_composer.build_prompt()
    gr.Info("✨ Prompt built from tags!")
    return prompt


def clear_all_tags(prompt_composer):
    """
    Clear all selected tags.

    Args:
        prompt_composer: PromptComposer instance

    Returns:
        tuple: (selected_tags_display, built_prompt)
    """
    prompt_composer.clear_tags()
    gr.Info("🗑️ All tags cleared")
    return prompt_composer.get_selected_tags_display(), ""


def load_template_handler(template_name, prompt_composer):
    """
    Load a template.

    Args:
        template_name: Template name (includes description)
        prompt_composer: PromptComposer instance

    Returns:
        tuple: (selected_tags_display, built_prompt)
    """
    if not template_name:
        return "", ""

    # Find template by name (template_name includes description)
    template_name_only = template_name.split(" - ")[0]
    for template in prompt_composer.get_all_templates():
        if template.name == template_name_only:
            prompt = prompt_composer.load_template(template)
            gr.Info(f"📥 Loaded template: {template.name}")
            return prompt_composer.get_selected_tags_display(), prompt

    return "", ""


def copy_to_main_prompt(built):
    """
    Copy built prompt to main prompt editor.

    Args:
        built: Built prompt text

    Returns:
        str: Prompt text or empty string
    """
    if built:
        gr.Info("➡️ Prompt copied to editor!")
        return built
    return ""


def save_custom_template(name, desc, category, prompt_composer):
    """
    Save current composition as template.

    Args:
        name: Template name
        desc: Template description
        category: Template category
        prompt_composer: PromptComposer instance

    Returns:
        gr.update: Save status update
    """
    if not name:
        gr.Warning("Please enter a template name")
        return gr.update(value="⚠️ Please enter a template name", visible=True)

    try:
        prompt_composer.save_as_template(name, desc, category)
        gr.Info(f"💾 Saved template: {name}")
        return gr.update(value=f"✅ Template saved: {name}", visible=True)
    except Exception as e:
        gr.Error(f"Failed to save template: {e}")
        return gr.update(value=f"❌ Error: {e}", visible=True)


def open_image_preview(image, gallery):
    """
    Open full-size preview of generated image.

    Args:
        image: Image to preview
        gallery: ImageGallery instance

    Returns:
        tuple: (accordion_update, preview_image, preview_metadata)
    """
    if image is None:
        return gr.update(visible=False), gr.update(), gr.update()

    # Get metadata
    last_meta = gallery.get_last_image_metadata()
    if last_meta:
        meta_display = f"""
        <div class="metadata-row">
            <span class="metadata-label">Prompt:</span>
            <span class="metadata-value">{last_meta.get('prompt', 'N/A')}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Seed:</span>
            <span class="metadata-value">{last_meta.get('seed', 'N/A')}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Dimensions:</span>
            <span class="metadata-value">{last_meta.get('width', 'N/A')} × {last_meta.get('height', 'N/A')}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Steps:</span>
            <span class="metadata-value">{last_meta.get('steps', 'N/A')}</span>
        </div>
        """
    else:
        meta_display = "No metadata available"

    return (
        gr.update(visible=True, open=True),  # accordion
        image,  # preview_image
        meta_display,  # preview_metadata
    )


def close_image_preview():
    """
    Close image preview accordion.

    Returns:
        gr.update: Accordion update to hide and close
    """
    return gr.update(visible=False, open=False)
