"""
UI Component: Generation Settings

This module provides the generation settings UI for the AI Image Chat application.
Includes parameter controls, workflow selection, and statistics display.
"""

import gradio as gr


def create_generation_settings(
    workflow_manager, session_stats, default_config: dict
) -> dict[str, gr.components.Component]:
    """
    Create the generation settings UI component.

    This component includes:
    - Generation Settings accordion with tabs:
      - Basic: Steps, width, height sliders
      - Advanced: Seed management with history and variations
      - Img2img: Input image and denoise strength
    - Workflow selector accordion:
      - Category filter
      - Workflow dropdown
      - Import/export functionality
    - Statistics accordion:
      - Session stats display

    Parameters
    ----------
    workflow_manager : WorkflowManager
        The workflow manager instance for loading workflows
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
        Dictionary containing generation settings components with keys:

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

        Workflow:
        - 'workflow_dropdown': Workflow selector dropdown
        - 'workflow_refresh_btn': Refresh workflows button
        - 'workflow_category_filter': Category filter dropdown
        - 'workflow_info': Workflow info markdown
        - 'workflow_upload_file': Upload workflow file
        - 'workflow_import_btn': Import workflow button
        - 'workflow_export_btn': Export workflow button

        Statistics:
        - 'stats_display': Session stats markdown

    Examples
    --------
    >>> from core import WorkflowManager, SessionStats
    >>> from config import DEFAULT_STEPS, DEFAULT_WIDTH, DEFAULT_HEIGHT
    >>> config = {
    ...     'DEFAULT_STEPS': DEFAULT_STEPS,
    ...     'DEFAULT_WIDTH': DEFAULT_WIDTH,
    ...     'DEFAULT_HEIGHT': DEFAULT_HEIGHT
    ... }
    >>> components = create_generation_settings(workflow_manager, session_stats, config)
    >>> steps_slider = components['steps_slider']
    >>> workflow_dropdown = components['workflow_dropdown']

    Notes
    -----
    - Event handlers must be wired up in the main app
    - The workflow manager and session stats must be initialized
    - Default config values are used for slider initial values
    """
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

    # Workflow Accordion
    current_workflow_name = (
        workflow_manager.get_current_workflow().metadata.name
        if workflow_manager.get_current_workflow()
        else "Default Workflow"
    )
    with gr.Accordion(f"🔀 Workflow", open=False):
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

    # Session Stats Display
    with gr.Accordion("📊 Statistics", open=False):
        stats_display = gr.Markdown(value=session_stats.get_stats_display())

    # Return all components as a dictionary
    return {
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
        # Workflow
        "workflow_dropdown": workflow_dropdown,
        "workflow_refresh_btn": workflow_refresh_btn,
        "workflow_category_filter": workflow_category_filter,
        "workflow_info": workflow_info,
        "workflow_upload_file": workflow_upload_file,
        "workflow_import_btn": workflow_import_btn,
        "workflow_export_btn": workflow_export_btn,
        # Statistics
        "stats_display": stats_display,
    }
