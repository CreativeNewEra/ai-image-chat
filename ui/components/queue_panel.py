"""
UI Component: Queue Panel

This module provides the batch generation queue UI for the AI Image Chat application.
Allows users to queue multiple generation jobs and process them sequentially.
"""

import gradio as gr


def create_queue_panel() -> dict[str, gr.components.Component]:
    """
    Create the batch generation queue panel UI component.

    This component includes:
    - Add to queue button
    - Add seed variations button with count slider
    - Queue status display
    - Process queue button
    - Clear completed/cancel all buttons

    Parameters
    ----------
    None

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing queue panel components with keys:

        Queue Controls:
        - 'add_queue_btn': Add to queue button
        - 'batch_variations_btn': Add seed variations button
        - 'variation_count': Variation count slider
        - 'queue_status': Queue status textbox
        - 'process_queue_btn': Process next job button
        - 'clear_completed_btn': Clear completed jobs button
        - 'cancel_all_btn': Cancel all pending jobs button

    Examples
    --------
    >>> components = create_queue_panel()
    >>> add_queue_btn = components['add_queue_btn']
    >>> queue_status = components['queue_status']

    Notes
    -----
    - Event handlers must be wired up in the main app
    - Queue management logic is handled in core.generation_queue module
    - This UI should be placed in an accordion or collapsible section
    """
    with gr.Accordion(f"🔄 Batch Queue", open=False):
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

    # Return all components as a dictionary
    return {
        "add_queue_btn": add_queue_btn,
        "batch_variations_btn": batch_variations_btn,
        "variation_count": variation_count,
        "queue_status": queue_status,
        "process_queue_btn": process_queue_btn,
        "clear_completed_btn": clear_completed_btn,
        "cancel_all_btn": cancel_all_btn,
    }
