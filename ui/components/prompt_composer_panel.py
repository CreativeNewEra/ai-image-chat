"""
UI Component: Prompt Composer Panel

This module provides the prompt composition UI for building prompts with tags and templates.
"""

import gradio as gr


def create_prompt_composer(composer) -> dict[str, gr.components.Component]:
    """
    Create the prompt composer UI component.

    This component includes:
    - Tag browser organized by category (tabs)
    - Selected tags display
    - Template library with preview
    - Build/Clear/Save actions
    - Generated prompt display

    Parameters
    ----------
    composer : PromptComposer
        The prompt composer instance

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing all composer-related components

    Examples
    --------
    >>> from core import PromptComposer
    >>> composer = PromptComposer()
    >>> components = create_prompt_composer(composer)
    >>> # Access individual components
    >>> tag_display = components['selected_tags_display']
    >>> built_prompt = components['built_prompt']

    Notes
    -----
    - This component should be placed in an accordion in the generation panel
    - Event handlers must be wired up in the main app
    - Tags are clickable buttons that add to the selection
    """

    gr.Markdown("### 🎨 Prompt Composer")
    gr.Markdown("Build better prompts using tags and templates")

    # ========================================
    # TEMPLATE LIBRARY SECTION
    # ========================================

    with gr.Accordion("📚 Template Library", open=True):
        gr.Markdown("**Quick Start** - Load a pre-made template")

        # Template category filter
        template_categories = ["All"] + composer.get_template_categories()
        template_category_filter = gr.Dropdown(
            choices=template_categories,
            value="All",
            label="Filter by Category",
            scale=1,
        )

        # Template selector
        all_templates = composer.get_all_templates()
        template_choices = [
            f"{t.name} - {t.description}" for t in all_templates
        ]
        template_selector = gr.Dropdown(
            choices=template_choices,
            label="Select Template",
            info="Choose a template to load its tags",
        )

        # Template actions
        with gr.Row():
            load_template_btn = gr.Button("📥 Load Template", variant="primary")
            view_template_btn = gr.Button("👁️ Preview", variant="secondary")

        # Template preview
        template_preview = gr.Markdown(value="", visible=False)

    # ========================================
    # TAG BROWSER SECTION
    # ========================================

    with gr.Accordion("🏷️ Tag Browser", open=False):
        gr.Markdown("**Build Custom** - Click tags to add them to your prompt")

        # Tabs for each tag category
        with gr.Tabs() as tag_tabs:
            tag_buttons = {}

            # Subject tags
            with gr.Tab("🎭 Subject"):
                subject_tags = composer.get_tags_by_category("subject")
                with gr.Row():
                    for tag in subject_tags:
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

            # Style tags
            with gr.Tab("🖌️ Style"):
                style_tags = composer.get_tags_by_category("style")
                with gr.Row():
                    for i, tag in enumerate(style_tags):
                        if i > 0 and i % 4 == 0:
                            gr.Row()
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

            # Lighting tags
            with gr.Tab("💡 Lighting"):
                lighting_tags = composer.get_tags_by_category("lighting")
                with gr.Row():
                    for tag in lighting_tags:
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

            # Mood tags
            with gr.Tab("🎭 Mood"):
                mood_tags = composer.get_tags_by_category("mood")
                with gr.Row():
                    for tag in mood_tags:
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

            # Camera tags
            with gr.Tab("📷 Camera"):
                camera_tags = composer.get_tags_by_category("camera")
                with gr.Row():
                    for tag in camera_tags:
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

            # Quality tags
            with gr.Tab("✨ Quality"):
                quality_tags = composer.get_tags_by_category("quality")
                with gr.Row():
                    for tag in quality_tags:
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

            # Color tags
            with gr.Tab("🎨 Colors"):
                color_tags = composer.get_tags_by_category("colors")
                with gr.Row():
                    for tag in color_tags:
                        btn = gr.Button(tag.name, size="sm")
                        tag_buttons[tag.name] = (btn, tag)

    # ========================================
    # SELECTED TAGS & PROMPT BUILD SECTION
    # ========================================

    with gr.Row():
        gr.Markdown("**Selected Tags:**")

    selected_tags_display = gr.Markdown(
        value=composer.get_selected_tags_display(),
        elem_classes=["composer-tags-display"]
    )

    with gr.Row():
        build_prompt_btn = gr.Button("✨ Build Prompt", variant="primary", size="lg")
        clear_tags_btn = gr.Button("🗑️ Clear All Tags", variant="secondary")

    built_prompt = gr.Textbox(
        label="Generated Prompt",
        placeholder="Your prompt will appear here...",
        lines=3,
        interactive=False,
    )

    # ========================================
    # SAVE CUSTOM TEMPLATE SECTION
    # ========================================

    with gr.Accordion("💾 Save as Custom Template", open=False):
        gr.Markdown("Save your current composition for reuse")

        template_name_input = gr.Textbox(
            label="Template Name",
            placeholder="My Custom Template",
        )

        template_desc_input = gr.Textbox(
            label="Description",
            placeholder="Describe this template...",
        )

        template_category_input = gr.Textbox(
            label="Category",
            placeholder="custom",
            value="custom",
        )

        save_template_btn = gr.Button("💾 Save Template", variant="primary")

        save_status = gr.Markdown(value="", visible=False)

    # ========================================
    # QUICK ACTIONS
    # ========================================

    with gr.Row():
        copy_to_prompt_btn = gr.Button(
            "➡️ Copy to Prompt Editor",
            variant="primary",
            size="lg"
        )

    # Return all components
    return {
        # Template library
        "template_category_filter": template_category_filter,
        "template_selector": template_selector,
        "load_template_btn": load_template_btn,
        "view_template_btn": view_template_btn,
        "template_preview": template_preview,
        # Tag browser
        "tag_tabs": tag_tabs,
        "tag_buttons": tag_buttons,  # Dict of {tag_name: (button, tag_object)}
        # Selected tags & build
        "selected_tags_display": selected_tags_display,
        "build_prompt_btn": build_prompt_btn,
        "clear_tags_btn": clear_tags_btn,
        "built_prompt": built_prompt,
        # Save template
        "template_name_input": template_name_input,
        "template_desc_input": template_desc_input,
        "template_category_input": template_category_input,
        "save_template_btn": save_template_btn,
        "save_status": save_status,
        # Quick actions
        "copy_to_prompt_btn": copy_to_prompt_btn,
    }
