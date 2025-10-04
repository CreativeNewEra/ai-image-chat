# UI Components Module

This module contains reusable UI component builders for the AI Image Chat application. All UI components have been extracted from `app.py` for better maintainability, reusability, and separation of concerns.

## Architecture Overview

```
ui/components/
├── __init__.py           # Module exports and documentation
├── mode_selector.py      # Mode selection and status display
├── chat_interface.py     # Text and Vision chat interfaces
├── generation_panel.py   # Image generation controls and settings
├── gallery_view.py       # Session gallery with filtering/sorting
└── README.md            # This file
```

## Component Files

### `mode_selector.py`

**Purpose:** Provides mode selection radio buttons and status display for switching between Idle, Text Chat, Vision Chat, and Generate modes.

**Function:** `create_mode_selector() -> tuple`

**Returns:**
- `mode_radio` (gr.Radio): Radio buttons for mode selection
- `mode_status` (gr.Markdown): Status display for current mode and VRAM info
- `check_status_btn` (gr.Button): Refresh status button
- `auto_switch_checkbox` (gr.Checkbox): Smart suggestions toggle
- `shortcuts_help` (gr.Accordion): Keyboard shortcuts help (currently disabled)

**Usage:**
```python
from ui.components import create_mode_selector

# Create the component
mode_radio, mode_status, check_btn, auto_switch, shortcuts = create_mode_selector()

# Set initial status value
mode_status.value = mode_manager._get_status_message()

# Wire up event handlers
mode_radio.change(fn=handle_mode_change, inputs=[mode_radio], outputs=[mode_status])
```

**Integration:** Works with `ModeManager` from `core.mode_manager` for mode switching logic.

---

### `chat_interface.py`

**Purpose:** Provides tabbed interface for Text Chat and Vision Chat with Ollama integration.

**Function:** `create_chat_interface(available_models: list[str], default_model: str) -> dict`

**Parameters:**
- `available_models`: List of available Ollama models
- `default_model`: Default model to select (from `config.OLLAMA_CHAT_MODEL`)

**Returns Dictionary Keys:**
- `model_dropdown`: Dropdown for selecting chat model
- `refresh_models_btn`: Button to refresh model list
- `chatbot`: Text chat history display
- `msg`: Text chat message input
- `send_btn`: Text chat send button
- `clear_chat_btn`: Clear text chat button
- `vision_chatbot`: Vision chat history display
- `vision_image_preview`: Image preview in vision chat
- `vision_msg`: Vision chat message input
- `vision_send_btn`: Vision chat send button
- `clear_vision_btn`: Clear vision chat button

**Usage:**
```python
from ui.components import create_chat_interface
from config import OLLAMA_CHAT_MODEL

# Create the component
chat_components = create_chat_interface(
    available_models=get_available_models(),
    default_model=OLLAMA_CHAT_MODEL
)

# Access individual components
chatbot = chat_components['chatbot']
send_btn = chat_components['send_btn']

# Wire up event handlers
send_btn.click(fn=chat_handler, inputs=[chat_components['msg']], outputs=[chatbot])
```

**Integration:** Works with Ollama API for chat functionality and prompt extraction.

---

### `generation_panel.py`

**Purpose:** Provides all image generation controls, settings, workflow management, and batch queue.

**Function:** `create_generation_panel(workflow_manager, prompt_history, session_stats, default_config: dict) -> dict`

**Parameters:**
- `workflow_manager`: WorkflowManager instance
- `prompt_history`: PromptHistory instance
- `session_stats`: SessionStats instance
- `default_config`: Dictionary with `DEFAULT_STEPS`, `DEFAULT_WIDTH`, `DEFAULT_HEIGHT`

**Returns Dictionary Keys:**

**Quick Actions:**
- `quick_generate_btn`, `quick_copy_btn`, `quick_clear_btn`, `quick_extract_btn`

**Prompt:**
- `prompt_display`, `extract_prompt_btn`, `copy_prompt_btn`, `clear_prompt_btn`

**Prompt History:**
- `prompt_search`, `search_btn`, `prompt_history_dropdown`, `load_prompt_btn`, `refresh_history_btn`, `export_prompts_btn`, `import_file`, `history_status`

**Presets:**
- `preset_fast`, `preset_balanced`, `preset_quality`, `preset_ultra`

**Workflow:**
- `workflow_dropdown`, `workflow_refresh_btn`, `workflow_category_filter`, `workflow_info`, `workflow_upload_file`, `workflow_import_btn`, `workflow_export_btn`

**Settings:**
- `steps_slider`, `width_slider`, `height_slider`

**Seed:**
- `seed_input`, `seed_lock_checkbox`, `use_last_seed_btn`, `seed_random_btn`, `seed_minus_100_btn`, `seed_minus_10_btn`, `seed_minus_1_btn`, `seed_plus_1_btn`, `seed_plus_10_btn`, `seed_plus_100_btn`, `seed_history_dropdown`

**Img2Img:**
- `input_image`, `denoise_slider`

**Generation:**
- `generate_btn`, `vram_warning_display`, `generation_progress`, `generation_status`, `generated_image`, `stats_display`

**Batch Queue:**
- `add_queue_btn`, `batch_variations_btn`, `variation_count`, `queue_status`, `process_queue_btn`, `clear_completed_btn`, `cancel_all_btn`

**Usage:**
```python
from ui.components import create_generation_panel
from config import DEFAULT_STEPS, DEFAULT_WIDTH, DEFAULT_HEIGHT

# Create the component
gen_components = create_generation_panel(
    workflow_manager=workflow_manager,
    prompt_history=prompt_history,
    session_stats=session_stats,
    default_config={
        'DEFAULT_STEPS': DEFAULT_STEPS,
        'DEFAULT_WIDTH': DEFAULT_WIDTH,
        'DEFAULT_HEIGHT': DEFAULT_HEIGHT
    }
)

# Access individual components
generate_btn = gen_components['generate_btn']
prompt_display = gen_components['prompt_display']

# Wire up event handlers
generate_btn.click(fn=generate_image, inputs=[...], outputs=[...])
```

**Integration:** Works with `WorkflowManager`, `PromptHistory`, `SessionStats`, `SeedManager`, and `VRAMEstimator`.

---

### `gallery_view.py`

**Purpose:** Provides session gallery with filtering, sorting, and favorites functionality.

**Function:** `create_gallery_view() -> dict`

**Returns Dictionary Keys:**
- `gallery_filter`: Filter textbox for searching by keywords
- `gallery_sort`: Sort dropdown (newest, oldest, seed, resolution)
- `favorites_only_check`: Checkbox for showing favorites only
- `refresh_gallery_btn`: Refresh gallery button
- `gallery_stats_btn`: Show gallery statistics button
- `session_gallery`: Gallery component for displaying images
- `gallery_info`: Info textbox showing gallery status

**Usage:**
```python
from ui.components import create_gallery_view

# Create the component
gallery_components = create_gallery_view()

# Access individual components
gallery = gallery_components['session_gallery']
filter_box = gallery_components['gallery_filter']

# Wire up event handlers
filter_box.change(fn=update_gallery, inputs=[filter_box], outputs=[gallery])
```

**Integration:** Works with `ImageGallery` from `core.image_gallery` for gallery management.

---

## How to Add New Components

### 1. Create a New Component File

```python
# ui/components/my_new_component.py
"""
UI Component: My New Component

Description of what this component does.
"""

import gradio as gr

def create_my_new_component(param1, param2) -> dict[str, gr.components.Component]:
    """
    Create my new component UI.

    Parameters
    ----------
    param1 : type
        Description of param1
    param2 : type
        Description of param2

    Returns
    -------
    dict[str, gr.components.Component]
        Dictionary containing all component elements
    """
    # Create UI components
    component1 = gr.Button("Click Me")
    component2 = gr.Textbox(label="Input")

    # Return as dictionary
    return {
        "component1": component1,
        "component2": component2,
    }
```

### 2. Update `__init__.py`

```python
# Add import
from .my_new_component import create_my_new_component

# Add to __all__
__all__ = [
    "create_mode_selector",
    "create_chat_interface",
    "create_generation_panel",
    "create_gallery_view",
    "create_my_new_component",  # Add here
]
```

### 3. Update `ui/__init__.py`

```python
# Add to exports
from .components import (
    create_chat_interface,
    create_gallery_view,
    create_generation_panel,
    create_mode_selector,
    create_my_new_component,  # Add here
)

__all__ = [
    # ... existing exports
    "create_my_new_component",  # Add here
]
```

### 4. Use in `app.py`

```python
# Import
from ui.components import create_my_new_component

# Inside create_app():
my_components = create_my_new_component(param1, param2)
component1 = my_components['component1']
component2 = my_components['component2']

# Wire up event handlers
component1.click(fn=handler, inputs=[component2], outputs=[...])
```

---

## Component Design Patterns

### Return Type Pattern

All components follow the dictionary return pattern for flexibility:

```python
def create_component() -> dict[str, gr.components.Component]:
    """Component that returns dictionary."""
    button = gr.Button("Click")
    textbox = gr.Textbox("Text")

    return {
        "button": button,
        "textbox": textbox,
    }
```

**Why dictionaries?**
- Flexible: Easy to add/remove components without breaking API
- Self-documenting: Keys describe what each component is
- Easy to access: `components['button']` is clear and explicit

### Tuple Return Pattern (Legacy)

Some components use tuple returns for simplicity:

```python
def create_simple_component() -> tuple[gr.Button, gr.Textbox]:
    """Simple component with tuple return."""
    button = gr.Button("Click")
    textbox = gr.Textbox("Text")

    return button, textbox
```

**When to use tuples:**
- Very simple components (2-5 elements)
- Fixed number of return values
- Backward compatibility

### Parameter Pattern

Components should accept dependencies as parameters:

```python
def create_component(
    manager_instance,
    config: dict,
    optional_param: str = "default"
) -> dict:
    """
    Component with dependencies.

    Parameters
    ----------
    manager_instance : SomeManager
        Manager instance required for functionality
    config : dict
        Configuration dictionary
    optional_param : str, optional
        Optional parameter with default
    """
    # Use parameters to configure component
    value = config.get('key', 'default')

    # Create components using dependencies
    # ...
```

---

## Component Interaction Patterns

### Pattern 1: Direct Access

```python
# Create all components
mode_components = create_mode_selector()
chat_components = create_chat_interface(models, default)

# Extract for event handlers
mode_radio = mode_components[0]  # Tuple access
chatbot = chat_components['chatbot']  # Dict access

# Wire up
mode_radio.change(fn=handler, inputs=[mode_radio], outputs=[...])
```

### Pattern 2: Cross-Component Communication

```python
# Components can interact via event handlers
gen_components = create_generation_panel(...)
gallery_components = create_gallery_view()

# Generation updates gallery
gen_components['generate_btn'].click(
    fn=generate_image,
    outputs=[gen_components['generated_image']]
).then(
    fn=update_gallery,
    outputs=[gallery_components['session_gallery']]
)
```

### Pattern 3: Shared State

```python
# Components share state via Gradio State components
current_image = gr.State(None)

# Component 1 updates state
gen_components['generate_btn'].click(
    fn=generate,
    outputs=[gen_components['generated_image'], current_image]
)

# Component 2 uses state
chat_components['vision_send_btn'].click(
    fn=vision_chat,
    inputs=[chat_components['vision_msg'], current_image],
    outputs=[...]
)
```

---

## Testing Components

Components can be tested independently:

```python
# test_ui_components.py
from ui.components import create_mode_selector

def test_mode_selector_creation():
    """Test that mode selector creates all components."""
    result = create_mode_selector()

    # Check tuple length
    assert len(result) == 5

    # Check types
    mode_radio, mode_status, check_btn, auto_switch, shortcuts = result
    assert isinstance(mode_radio, gr.Radio)
    assert isinstance(mode_status, gr.Markdown)
    # ... more assertions
```

---

## Best Practices

1. **Comprehensive Docstrings**: All components should have detailed docstrings with:
   - Purpose description
   - Parameter documentation
   - Return value documentation
   - Usage examples
   - Integration notes

2. **Consistent Naming**: Follow naming conventions:
   - Functions: `create_*_component` or `create_*_panel`
   - Return keys: Clear, descriptive names (e.g., `generate_btn`, not `btn1`)
   - Files: Lowercase with underscores (e.g., `mode_selector.py`)

3. **Dependency Injection**: Pass dependencies as parameters rather than importing globally:
   ```python
   # Good
   def create_component(manager, config):
       value = config['key']

   # Avoid
   def create_component():
       from config import KEY
       value = KEY
   ```

4. **Single Responsibility**: Each component file should have one clear purpose:
   - `mode_selector.py` → Only mode selection UI
   - `chat_interface.py` → Only chat UI
   - Don't mix unrelated UI elements

5. **No Business Logic**: Components should only create UI, not implement logic:
   ```python
   # Good - just UI
   def create_component():
       button = gr.Button("Generate")
       return {"button": button}

   # Avoid - contains logic
   def create_component():
       button = gr.Button("Generate")
       button.click(fn=complex_logic)  # Wire in app.py instead
       return {"button": button}
   ```

6. **Return Flexibility**: Prefer dictionaries for components with many elements:
   - 1-3 elements: Tuple is fine
   - 4+ elements: Use dictionary

---

## Migration Guide

If you're updating existing code to use these components:

### Before (Old Pattern):
```python
# In app.py
with gr.Column():
    mode_radio = gr.Radio(choices=[...])
    mode_status = gr.Markdown(...)
    # ... 50 more lines of UI code
```

### After (New Pattern):
```python
# In app.py
from ui.components import create_mode_selector

mode_radio, mode_status, check_btn, auto_switch, shortcuts = create_mode_selector()
```

**Benefits:**
- Cleaner app.py (50 lines → 1 line)
- Reusable component
- Easier to test
- Better documentation

---

## Future Enhancements

Potential improvements to consider:

1. **Unit Tests**: Add comprehensive tests for each component
2. **Theme Support**: Make components theme-aware
3. **Component Variants**: Create variations (compact, expanded, minimal)
4. **Accessibility**: Add ARIA labels and keyboard navigation
5. **Custom Styling**: Add CSS class parameters for customization
6. **Component Composition**: Create higher-order components

---

## Troubleshooting

### Component Not Rendering

**Problem:** Component doesn't appear in UI

**Solution:**
- Check that component is returned from `create_*` function
- Verify component is placed inside `with gr.Blocks()` context
- Ensure all dependencies are imported

### Event Handler Not Working

**Problem:** Button click or input change doesn't trigger

**Solution:**
- Verify event handler is wired after component creation
- Check that component variable name matches the one used in `.click()`
- Ensure input/output components are passed correctly

### Import Errors

**Problem:** `ImportError: cannot import name 'create_*'`

**Solution:**
- Check `__all__` in `ui/components/__init__.py`
- Verify function name matches in component file
- Ensure `ui/__init__.py` exports the component

---

## Additional Resources

- **[CLAUDE.md](../../CLAUDE.md)** - Complete developer guide
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)** - Contribution guidelines
- **[app.py](../../app.py)** - Main application showing component usage
- **[core/](../../core/)** - Business logic modules that components integrate with
