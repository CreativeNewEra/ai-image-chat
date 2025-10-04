"""
UI Components Module

This module contains reusable UI component builders for the AI Image Chat application.
Extracted from app.py for better maintainability and separation of concerns.

Components
----------
- mode_selector: Mode selection radio buttons with status display
- chat_interface: Text Chat and Vision Chat tabbed interface
- generation_controls: Main generation UI (prompt, presets, generate button, image display)
- generation_settings: Generation parameters (steps, seed, workflow, img2img)
- queue_panel: Batch generation queue management
- gallery_view: Session gallery with filtering and sorting
- theme_settings: Theme customization panel
- prompt_composer_panel: Tag-based prompt building UI

Usage
-----
>>> from ui.components import (
...     create_mode_selector,
...     create_chat_interface,
...     create_generation_controls,
...     create_generation_settings,
...     create_queue_panel,
...     create_gallery_view
... )
>>> # Create mode selector
>>> mode_radio, mode_status, check_btn, auto_switch, shortcuts = create_mode_selector()
>>> # Create chat interface
>>> chat_components = create_chat_interface(available_models, default_model)
>>> # Create generation controls
>>> gen_controls = create_generation_controls(prompt_history, config)
>>> # Create generation settings
>>> gen_settings = create_generation_settings(workflow_manager, session_stats, config)
>>> # Create queue panel
>>> queue = create_queue_panel()
>>> # Create gallery view
>>> gallery_components = create_gallery_view()
"""

from .chat_interface import create_chat_interface
from .gallery_view import create_gallery_view
from .generation_controls import create_generation_controls
from .generation_settings import create_generation_settings
from .queue_panel import create_queue_panel
from .mode_selector import create_mode_selector
from .theme_settings import create_theme_settings
from .prompt_composer_panel import create_prompt_composer

__all__ = [
    "create_mode_selector",
    "create_chat_interface",
    "create_generation_controls",
    "create_generation_settings",
    "create_queue_panel",
    "create_gallery_view",
    "create_theme_settings",
    "create_prompt_composer",
]
