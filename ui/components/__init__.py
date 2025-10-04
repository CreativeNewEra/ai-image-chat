"""
UI Components Module

This module contains reusable UI component builders for the AI Image Chat application.
Extracted from app.py for better maintainability and separation of concerns.

Components
----------
- mode_selector: Mode selection radio buttons with status display
- chat_interface: Text Chat and Vision Chat tabbed interface
- generation_panel: Image generation controls and settings
- gallery_view: Session gallery with filtering and sorting

Usage
-----
>>> from ui.components import (
...     create_mode_selector,
...     create_chat_interface,
...     create_generation_panel,
...     create_gallery_view
... )
>>> # Create mode selector
>>> mode_radio, mode_status, check_btn, auto_switch, shortcuts = create_mode_selector()
>>> # Create chat interface
>>> chat_components = create_chat_interface(available_models, default_model)
>>> # Create generation panel
>>> gen_components = create_generation_panel(workflow_manager, prompt_history, session_stats, config)
>>> # Create gallery view
>>> gallery_components = create_gallery_view()
"""

from .chat_interface import create_chat_interface
from .gallery_view import create_gallery_view
from .generation_panel import create_generation_panel
from .mode_selector import create_mode_selector
from .theme_settings import create_theme_settings
from .prompt_composer_panel import create_prompt_composer

__all__ = [
    "create_mode_selector",
    "create_chat_interface",
    "create_generation_panel",
    "create_gallery_view",
    "create_theme_settings",
    "create_prompt_composer",
]
