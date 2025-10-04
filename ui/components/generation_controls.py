"""
UI Component: Generation Controls

This module provides the main generation controls UI for the AI Image Chat application.
Includes prompt editor, quick actions, presets, generate button, and image display.
"""

import gradio as gr


def create_generation_controls(prompt_history, default_config: dict) -> dict[str, gr.components.Component]:
    """
    Create the main generation controls UI component.

    This component includes:
    - Quick actions toolbar (generate, copy, clear, extract)
    - Prompt editor and display
    - Prompt history with search/export/import
    - Generation presets (Fast, Balanced, Quality, Ultra)
    - VRAM warning display
    - Generate button with progress bar
    - Generated image display
    - Image action buttons (variations, refine, favorite, copy seed)

    Parameters
    ----------
    prompt_history : PromptHistory
        The prompt history manager instance
    default_config : dict
        Dictionary with default configuration values (not currently used here)

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing generation control components with keys:

        Quick Actions:
        - 'quick_generate_btn': Quick generate button
        - 'quick_copy_btn': Quick copy button
        - 'quick_clear_btn': Quick clear button
        - 'quick_extract_btn': Quick extract button

        Prompt:
        - 'prompt_display': Main prompt textbox
        - 'extract_prompt_btn': Extract from chat button
        - 'copy_prompt_btn': Copy prompt button
        - 'clear_prompt_btn': Clear prompt button

        Prompt History:
        - 'prompt_search': Search textbox
        - 'search_btn': Search button
        - 'prompt_history_dropdown': History dropdown
        - 'load_prompt_btn': Load selected button
        - 'refresh_history_btn': Refresh history button
        - 'export_prompts_btn': Export history button
        - 'import_file': Import file uploader
        - 'history_status': History status textbox

        Presets:
        - 'preset_fast': Fast draft preset button
        - 'preset_balanced': Balanced preset button
        - 'preset_quality': High quality preset button
        - 'preset_ultra': Ultra detail preset button

        Generation:
        - 'generate_btn': Generate image button
        - 'vram_warning_display': VRAM warning markdown
        - 'generation_progress': Progress HTML
        - 'generation_status': Status textbox
        - 'generated_image': Generated image display

        Image Actions:
        - 'gen_variations_btn': Generate variations button
        - 'gen_refine_btn': Refine in vision chat button
        - 'gen_favorite_btn': Mark as favorite button
        - 'gen_copy_seed_btn': Copy seed button

    Examples
    --------
    >>> from core import PromptHistory
    >>> from config import DEFAULT_STEPS, DEFAULT_WIDTH, DEFAULT_HEIGHT
    >>> config = {
    ...     'DEFAULT_STEPS': DEFAULT_STEPS,
    ...     'DEFAULT_WIDTH': DEFAULT_WIDTH,
    ...     'DEFAULT_HEIGHT': DEFAULT_HEIGHT
    ... }
    >>> components = create_generation_controls(prompt_history, config)
    >>> generate_btn = components['generate_btn']
    >>> prompt_display = components['prompt_display']

    Notes
    -----
    - Event handlers must be wired up in the main app
    - The prompt history must be initialized before calling this function
    """
    gr.Markdown(
        '<div class="section-header">🎨 Image Generation</div>',
        elem_classes=["section-card"],
    )

    # Quick Actions Toolbar
    with gr.Row():
        quick_generate_btn = gr.Button("⚡ Quick Generate", size="sm", variant="primary")
        quick_copy_btn = gr.Button("📋 Copy", size="sm")
        quick_clear_btn = gr.Button("🗑️ Clear", size="sm")
        quick_extract_btn = gr.Button("📝 Extract", size="sm")

    # Prompt Editor
    prompt_display = gr.Textbox(
        label="Current Prompt",
        placeholder="Prompt will appear here after chatting...",
        lines=6,
        interactive=True,
    )

    with gr.Row():
        extract_prompt_btn = gr.Button("📝 Extract from Chat", size="sm")
        copy_prompt_btn = gr.Button("📋 Copy Prompt", size="sm")
        clear_prompt_btn = gr.Button("🗑️ Clear", size="sm")

    # Prompt History Section
    with gr.Accordion("📚 Prompt & History", open=False):
        gr.Markdown("**Prompt History** - Search, load, and manage your prompts")

        with gr.Row():
            prompt_search = gr.Textbox(placeholder="Search prompts...", label="Search", scale=3)
            search_btn = gr.Button("🔍 Search", size="sm", scale=1)

        prompt_history_dropdown = gr.Dropdown(
            label="Recent Prompts",
            choices=prompt_history.get_dropdown_choices(),
            value=None,
            interactive=True,
            allow_custom_value=False,
        )

        with gr.Row():
            load_prompt_btn = gr.Button("📥 Load Selected", size="sm")
            refresh_history_btn = gr.Button("🔄 Refresh", size="sm")

        with gr.Row():
            export_prompts_btn = gr.Button("💾 Export History", size="sm")
            import_file = gr.File(label="Import History", file_types=[".json"], type="filepath")

        history_status = gr.Textbox(label="Status", value="", interactive=False, visible=False)

    # Generation Presets
    gr.Markdown("**⚡ Quick Presets**")
    with gr.Row():
        preset_fast = gr.Button("⚡ Fast Draft\n768×768, 12 steps", size="sm")
        preset_balanced = gr.Button("⚖️ Balanced\n1024×1024, 20 steps", size="sm")
    with gr.Row():
        preset_quality = gr.Button("✨ High Quality\n1024×1024, 30 steps", size="sm")
        preset_ultra = gr.Button("🔥 Ultra Detail\n1536×1536, 40 steps", size="sm")

    # Generate Button
    generate_btn = gr.Button(
        "🎨 Generate Image",
        variant="primary",
        size="lg",
        elem_classes=["primary-action"],
    )

    # VRAM Warning Display
    vram_warning_display = gr.Markdown(value="", visible=False)

    # Progress Bar
    generation_progress = gr.HTML(value="", visible=False, elem_classes=["progress-container"])

    # Status
    generation_status = gr.Textbox(
        label="Status", value="Ready when you are!", interactive=False
    )

    # Image Display
    generated_image = gr.Image(label="Generated Image", type="pil", interactive=False, height=400)

    # Image Action Buttons
    with gr.Row(elem_classes=["image-actions"]):
        gen_variations_btn = gr.Button(
            "🔄 Variations",
            size="sm",
            elem_classes=["image-action-btn", "btn-variations"]
        )
        gen_refine_btn = gr.Button(
            "👁️ Refine",
            size="sm",
            elem_classes=["image-action-btn", "btn-refine"]
        )
        gen_favorite_btn = gr.Button(
            "⭐ Favorite",
            size="sm",
            elem_classes=["image-action-btn", "btn-favorite"]
        )
        gen_copy_seed_btn = gr.Button(
            "📋 Copy Seed",
            size="sm",
            elem_classes=["image-action-btn", "btn-copy-seed"]
        )

    # Return all components as a dictionary
    return {
        # Quick Actions
        "quick_generate_btn": quick_generate_btn,
        "quick_copy_btn": quick_copy_btn,
        "quick_clear_btn": quick_clear_btn,
        "quick_extract_btn": quick_extract_btn,
        # Prompt
        "prompt_display": prompt_display,
        "extract_prompt_btn": extract_prompt_btn,
        "copy_prompt_btn": copy_prompt_btn,
        "clear_prompt_btn": clear_prompt_btn,
        # Prompt History
        "prompt_search": prompt_search,
        "search_btn": search_btn,
        "prompt_history_dropdown": prompt_history_dropdown,
        "load_prompt_btn": load_prompt_btn,
        "refresh_history_btn": refresh_history_btn,
        "export_prompts_btn": export_prompts_btn,
        "import_file": import_file,
        "history_status": history_status,
        # Presets
        "preset_fast": preset_fast,
        "preset_balanced": preset_balanced,
        "preset_quality": preset_quality,
        "preset_ultra": preset_ultra,
        # Generation
        "generate_btn": generate_btn,
        "vram_warning_display": vram_warning_display,
        "generation_progress": generation_progress,
        "generation_status": generation_status,
        "generated_image": generated_image,
        # Image Actions
        "gen_variations_btn": gen_variations_btn,
        "gen_refine_btn": gen_refine_btn,
        "gen_favorite_btn": gen_favorite_btn,
        "gen_copy_seed_btn": gen_copy_seed_btn,
    }
