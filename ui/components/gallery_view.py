"""
UI Component: Gallery View

This module provides the session gallery UI for the AI Image Chat application.
Extracted from app.py for better maintainability.
"""

import gradio as gr


def create_gallery_view() -> dict[str, gr.components.Component]:
    """
    Create the gallery view UI component with filtering and sorting controls.

    This component includes:
    - Gallery section header
    - Filter controls (search by prompt keywords)
    - Sort controls (newest, oldest, seed, resolution)
    - Favorites filter checkbox
    - Refresh and stats buttons
    - Gallery display grid
    - Gallery info display

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing all gallery-related components with keys:
        - 'gallery_filter': Filter textbox for searching by keywords
        - 'gallery_sort': Sort dropdown (newest, oldest, seed, resolution)
        - 'favorites_only_check': Checkbox for showing favorites only
        - 'refresh_gallery_btn': Refresh gallery button
        - 'gallery_stats_btn': Show gallery statistics button
        - 'session_gallery': Gallery component for displaying images
        - 'gallery_info': Info textbox showing gallery status

    Examples
    --------
    >>> components = create_gallery_view()
    >>> # Access individual components
    >>> gallery = components['session_gallery']
    >>> filter_box = components['gallery_filter']
    >>> # Wire up event handlers in main app
    >>> filter_box.change(fn=update_gallery, inputs=[filter_box], outputs=[gallery])

    Notes
    -----
    - This component is displayed in a modal overlay (gr.Modal)
    - Event handlers must be wired up in the main app
    - The gallery integrates with ImageGallery class from core.image_gallery
    - Clicking images in the gallery loads them into Vision Chat and closes the modal
    - Gallery supports filtering by prompt keywords, sorting, and favorites
    - Images are displayed in a 4-column grid with auto height
    - Modal can be opened from any mode without switching modes
    """
    # Gallery Controls
    with gr.Row(elem_classes=["gallery-controls"]):
        with gr.Column(scale=2):
            gallery_filter = gr.Textbox(
                label="🔍 Filter Images", placeholder="Search by prompt keywords...", value=""
            )
        with gr.Column(scale=1):
            gallery_sort = gr.Dropdown(
                label="📊 Sort By",
                choices=["newest", "oldest", "seed", "resolution"],
                value="newest",
            )
        with gr.Column(scale=1):
            favorites_only_check = gr.Checkbox(label="⭐ Favorites Only", value=False)

    with gr.Row():
        refresh_gallery_btn = gr.Button("🔄 Refresh Gallery")
        gallery_stats_btn = gr.Button("📊 Gallery Stats")

    with gr.Row():
        session_gallery = gr.Gallery(
            label="Generated Images (click to load into Vision Chat)",
            show_label=True,
            elem_id="gallery",
            columns=4,
            rows=2,
            height="auto",
            object_fit="contain",
        )

    with gr.Row():
        gallery_info = gr.Textbox(
            label="Gallery Info",
            value="No images generated yet this session",
            interactive=False,
        )

    # Return all components as a dictionary
    return {
        "gallery_filter": gallery_filter,
        "gallery_sort": gallery_sort,
        "favorites_only_check": favorites_only_check,
        "refresh_gallery_btn": refresh_gallery_btn,
        "gallery_stats_btn": gallery_stats_btn,
        "session_gallery": session_gallery,
        "gallery_info": gallery_info,
    }
