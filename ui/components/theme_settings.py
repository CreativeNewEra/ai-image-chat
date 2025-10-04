"""
UI Component: Theme Settings Panel

This module provides the theme customization UI for the AI Image Chat application.
"""

import gradio as gr


def create_theme_settings(theme_manager) -> dict[str, gr.components.Component]:
    """
    Create the theme settings UI component.

    This component includes:
    - Theme mode selector (Light/Dark/Auto)
    - Color scheme selector
    - Layout density selector
    - Current theme display
    - Reset to defaults button

    Parameters
    ----------
    theme_manager : ThemeManager
        The theme manager instance

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing all theme-related components with keys:
        - 'theme_mode': Mode selector (light/dark/auto)
        - 'color_scheme': Color scheme dropdown
        - 'layout_density': Density selector (compact/comfortable/spacious)
        - 'theme_display': Current theme info display
        - 'reset_theme_btn': Reset to defaults button
        - 'apply_theme_btn': Apply theme button

    Examples
    --------
    >>> from core import ThemeManager
    >>> theme_manager = ThemeManager()
    >>> components = create_theme_settings(theme_manager)
    >>> # Access individual components
    >>> theme_mode = components['theme_mode']
    >>> color_scheme = components['color_scheme']

    Notes
    -----
    - This component should be placed in a settings accordion or modal
    - Event handlers must be wired up in the main app
    - Theme changes apply immediately when selections change
    """

    gr.Markdown("### 🎨 Theme Customization")
    gr.Markdown("Personalize your AI Image Chat experience")

    # Theme Mode Selector
    with gr.Row():
        theme_mode = gr.Radio(
            choices=["light", "dark", "auto"],
            value=theme_manager.get_mode(),
            label="🌓 Theme Mode",
            info="Auto follows your system preference",
        )

    # Color Scheme Selector
    with gr.Row():
        scheme_choices = theme_manager.get_all_color_schemes()
        scheme_names = [name for _, name in scheme_choices]
        scheme_values = [key for key, _ in scheme_choices]

        # Map current scheme to display name
        current_scheme = theme_manager.get_color_scheme()
        current_index = scheme_values.index(current_scheme) if current_scheme in scheme_values else 0

        color_scheme = gr.Dropdown(
            choices=scheme_names,
            value=scheme_names[current_index],
            label="🎨 Color Scheme",
            info="Choose your preferred color palette",
        )

    # Layout Density Selector
    with gr.Row():
        layout_density = gr.Radio(
            choices=["compact", "comfortable", "spacious"],
            value=theme_manager.get_layout_density(),
            label="📏 Layout Density",
            info="Adjust spacing and element sizes",
        )

    # Current Theme Display
    with gr.Row():
        theme_display = gr.Markdown(
            value=theme_manager.get_theme_display(),
            elem_classes=["theme-info-display"]
        )

    # Action Buttons
    with gr.Row():
        apply_theme_btn = gr.Button("✨ Apply Theme", variant="primary")
        reset_theme_btn = gr.Button("🔄 Reset to Defaults", variant="secondary")

    # Return all components
    return {
        "theme_mode": theme_mode,
        "color_scheme": color_scheme,
        "layout_density": layout_density,
        "theme_display": theme_display,
        "apply_theme_btn": apply_theme_btn,
        "reset_theme_btn": reset_theme_btn,
    }
