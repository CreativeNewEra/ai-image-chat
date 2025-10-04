"""
UI Component: Generation Panel

This module provides the image generation panel UI for the AI Image Chat application.
Extracted from app.py for better maintainability.
"""

import gradio as gr


def create_generation_panel(
    workflow_manager, prompt_history, session_stats, default_config: dict
) -> dict[str, gr.components.Component]:
    """
    Create the generation panel UI component with all controls.

    This component includes:
    - Quick actions toolbar (generate, copy, clear, extract)
    - Prompt editor and display
    - Prompt history with search/export/import
    - Generation presets (Fast, Balanced, Quality, Ultra)
    - Workflow selector with category filtering
    - Generation settings (steps, width, height)
    - Seed management with history and variations
    - Img2img settings (input image, denoise strength)
    - Generate button
    - VRAM warning display
    - Progress bar and status
    - Generated image display
    - Session statistics
    - Batch generation queue

    Parameters
    ----------
    workflow_manager : WorkflowManager
        The workflow manager instance for loading workflows
    prompt_history : PromptHistory
        The prompt history manager instance
    session_stats : SessionStats
        The session statistics manager instance
    default_config : dict
        Dictionary with default configuration values:
        - DEFAULT_STEPS: int
        - DEFAULT_WIDTH: int
        - DEFAULT_HEIGHT: int

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing all generation-related components with keys:

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

        Workflow:
        - 'workflow_dropdown': Workflow selector dropdown
        - 'workflow_refresh_btn': Refresh workflows button
        - 'workflow_category_filter': Category filter dropdown
        - 'workflow_info': Workflow info markdown
        - 'workflow_upload_file': Upload workflow file
        - 'workflow_import_btn': Import workflow button
        - 'workflow_export_btn': Export workflow button

        Settings:
        - 'steps_slider': Steps slider
        - 'width_slider': Width slider
        - 'height_slider': Height slider

        Seed:
        - 'seed_input': Seed input textbox
        - 'seed_lock_checkbox': Lock seed checkbox
        - 'use_last_seed_btn': Use last seed button
        - 'seed_random_btn': Random seed button
        - 'seed_minus_100_btn': Seed -100 button
        - 'seed_minus_10_btn': Seed -10 button
        - 'seed_minus_1_btn': Seed -1 button
        - 'seed_plus_1_btn': Seed +1 button
        - 'seed_plus_10_btn': Seed +10 button
        - 'seed_plus_100_btn': Seed +100 button
        - 'seed_history_dropdown': Seed history dropdown

        Img2Img:
        - 'input_image': Input image uploader
        - 'denoise_slider': Denoise strength slider

        Generation:
        - 'generate_btn': Generate image button
        - 'vram_warning_display': VRAM warning markdown
        - 'generation_progress': Progress HTML
        - 'generation_status': Status textbox
        - 'generated_image': Generated image display
        - 'stats_display': Session stats markdown

        Batch Queue:
        - 'add_queue_btn': Add to queue button
        - 'batch_variations_btn': Add seed variations button
        - 'variation_count': Variation count slider
        - 'queue_status': Queue status textbox
        - 'process_queue_btn': Process next job button
        - 'clear_completed_btn': Clear completed button
        - 'cancel_all_btn': Cancel all button

    Examples
    --------
    >>> from core import WorkflowManager, PromptHistory, SessionStats
    >>> from config import DEFAULT_STEPS, DEFAULT_WIDTH, DEFAULT_HEIGHT
    >>> config = {
    ...     'DEFAULT_STEPS': DEFAULT_STEPS,
    ...     'DEFAULT_WIDTH': DEFAULT_WIDTH,
    ...     'DEFAULT_HEIGHT': DEFAULT_HEIGHT
    ... }
    >>> components = create_generation_panel(workflow_manager, prompt_history, session_stats, config)
    >>> # Access individual components
    >>> generate_btn = components['generate_btn']
    >>> prompt_display = components['prompt_display']

    Notes
    -----
    - This component should be placed in the right column of the main interface
    - Event handlers must be wired up in the main app
    - The workflow manager, prompt history, and session stats must be initialized
    - Default config values are used for slider initial values
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

    # Consolidated Settings Accordion with Tabs
    with gr.Accordion("⚙️ Generation Settings", open=False):
        with gr.Tabs():
            # Basic Settings Tab
            with gr.Tab("📐 Basic"):
                with gr.Row():
                    steps_slider = gr.Slider(
                        minimum=4,
                        maximum=50,
                        value=default_config["DEFAULT_STEPS"],
                        step=1,
                        label="Steps (20 recommended for Krea)",
                    )

                with gr.Row():
                    width_slider = gr.Slider(
                        minimum=512,
                        maximum=2048,
                        value=default_config["DEFAULT_WIDTH"],
                        step=64,
                        label="Width",
                    )
                    height_slider = gr.Slider(
                        minimum=512,
                        maximum=2048,
                        value=default_config["DEFAULT_HEIGHT"],
                        step=64,
                        label="Height",
                    )

            # Advanced Settings Tab (Seed Management)
            with gr.Tab("🎲 Advanced"):
                gr.Markdown("**Seed Control** - Fine-tune generation randomness")

                with gr.Row():
                    seed_input = gr.Textbox(
                        label="Seed (leave empty for random)",
                        placeholder="Random seed",
                        value="",
                        scale=3,
                    )
                    seed_lock_checkbox = gr.Checkbox(label="🔒 Lock", value=False, info="Keep seed", scale=1)

                with gr.Row():
                    use_last_seed_btn = gr.Button("🔄 Use Last", size="sm")
                    seed_random_btn = gr.Button("🎲 Random", size="sm")

                gr.Markdown("**Fine Tune Seed:**")
                with gr.Row():
                    seed_minus_100_btn = gr.Button("−100", size="sm")
                    seed_minus_10_btn = gr.Button("−10", size="sm")
                    seed_minus_1_btn = gr.Button("−1", size="sm")
                    seed_plus_1_btn = gr.Button("+1", size="sm")
                    seed_plus_10_btn = gr.Button("+10", size="sm")
                    seed_plus_100_btn = gr.Button("+100", size="sm")

                with gr.Row():
                    seed_history_dropdown = gr.Dropdown(
                        label="Seed History",
                        choices=[],
                        value=None,
                        interactive=True,
                        allow_custom_value=True,
                    )

            # Img2Img Settings Tab
            with gr.Tab("🖼️ Img2Img"):
                gr.Markdown(
                    "Upload an image to modify it instead of generating from scratch. Workflow must support img2img (LoadImage + VAEEncode)."
                )

                input_image = gr.Image(
                    label="Input Image (leave empty for text2img)",
                    type="filepath",
                    interactive=True,
                )

                denoise_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.75,
                    step=0.05,
                    label="Denoise Strength",
                    info="0.0 = no change, 1.0 = complete regeneration",
                )

    # Workflow & Queue Accordion
    current_workflow_name = (
        workflow_manager.get_current_workflow().metadata.name
        if workflow_manager.get_current_workflow()
        else "Default Workflow"
    )
    with gr.Accordion(f"🔀 Workflow & Batch Queue", open=False):
        with gr.Tabs():
            # Workflow Tab
            with gr.Tab("🔀 Workflow"):
                gr.Markdown("Select a ComfyUI workflow to use for generation")

                with gr.Row():
                    workflow_dropdown = gr.Dropdown(
                        label="Workflow",
                        choices=[wf["name"] for wf in workflow_manager.get_workflows_list()],
                        value=(
                            workflow_manager.get_current_workflow().metadata.name
                            if workflow_manager.get_current_workflow()
                            else None
                        ),
                        interactive=True,
                        scale=3,
                    )
                    workflow_refresh_btn = gr.Button("🔄 Refresh", size="sm", scale=1)

                with gr.Row():
                    workflow_category_filter = gr.Dropdown(
                        label="Filter by Category",
                        choices=["All"] + workflow_manager.get_all_categories(),
                        value="All",
                        interactive=True,
                    )

                workflow_info = gr.Markdown(value="Loading workflow info...")

                with gr.Row():
                    workflow_upload_file = gr.File(
                        label="Upload Workflow JSON", file_types=[".json"], type="filepath"
                    )

                with gr.Row():
                    workflow_import_btn = gr.Button("📥 Import Workflow", size="sm")
                    workflow_export_btn = gr.Button("📤 Export Current", size="sm")

            # Batch Queue Tab
            with gr.Tab("🔄 Queue"):
                gr.Markdown("Add multiple prompts to a queue and process them sequentially")

                with gr.Row():
                    add_queue_btn = gr.Button("➕ Add to Queue", variant="secondary")
                    batch_variations_btn = gr.Button("🎲 Add 4 Seed Variations", variant="secondary")

                with gr.Row():
                    variation_count = gr.Slider(
                        minimum=2, maximum=10, value=4, step=1, label="Variation Count"
                    )

                queue_status = gr.Textbox(label="Queue Status", value="Queue is empty", interactive=False)

                with gr.Row():
                    process_queue_btn = gr.Button("▶️ Process Next Job", variant="primary")
                    clear_completed_btn = gr.Button("🗑️ Clear Completed")
                    cancel_all_btn = gr.Button("❌ Cancel All", variant="stop")

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

    # Session Stats Display
    with gr.Accordion("📊 Statistics", open=False):
        stats_display = gr.Markdown(value=session_stats.get_stats_display())

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
        # Workflow
        "workflow_dropdown": workflow_dropdown,
        "workflow_refresh_btn": workflow_refresh_btn,
        "workflow_category_filter": workflow_category_filter,
        "workflow_info": workflow_info,
        "workflow_upload_file": workflow_upload_file,
        "workflow_import_btn": workflow_import_btn,
        "workflow_export_btn": workflow_export_btn,
        # Settings
        "steps_slider": steps_slider,
        "width_slider": width_slider,
        "height_slider": height_slider,
        # Seed
        "seed_input": seed_input,
        "seed_lock_checkbox": seed_lock_checkbox,
        "use_last_seed_btn": use_last_seed_btn,
        "seed_random_btn": seed_random_btn,
        "seed_minus_100_btn": seed_minus_100_btn,
        "seed_minus_10_btn": seed_minus_10_btn,
        "seed_minus_1_btn": seed_minus_1_btn,
        "seed_plus_1_btn": seed_plus_1_btn,
        "seed_plus_10_btn": seed_plus_10_btn,
        "seed_plus_100_btn": seed_plus_100_btn,
        "seed_history_dropdown": seed_history_dropdown,
        # Img2Img
        "input_image": input_image,
        "denoise_slider": denoise_slider,
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
        "stats_display": stats_display,
        # Batch Queue
        "add_queue_btn": add_queue_btn,
        "batch_variations_btn": batch_variations_btn,
        "variation_count": variation_count,
        "queue_status": queue_status,
        "process_queue_btn": process_queue_btn,
        "clear_completed_btn": clear_completed_btn,
        "cancel_all_btn": cancel_all_btn,
    }
