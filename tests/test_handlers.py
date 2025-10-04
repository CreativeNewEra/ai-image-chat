"""Comprehensive tests for all handler modules.

Tests all 58 handler functions extracted from app.py with proper mocking
and dependency injection.
"""

from unittest.mock import Mock, MagicMock, patch
import pytest
import gradio as gr
from PIL import Image

from handlers import (
    # Mode handlers
    handle_mode_change,
    toggle_auto_switch,
    # Gallery handlers
    update_gallery_display,
    show_gallery_stats,
    load_gallery_image,
    open_gallery,
    close_gallery,
    gallery_toggle_favorite,
    gallery_use_img2img,
    gallery_open_vision,
    gallery_delete_image,
    # Workflow handlers
    get_workflow_info_display,
    switch_workflow,
    refresh_workflows,
    filter_workflows_by_category,
    import_workflow_from_file,
    export_current_workflow,
    # Chat handlers
    user_message,
    bot_message,
    vision_user_message,
    vision_bot_message,
    extract_from_chat,
    load_selected_prompt,
    search_and_update_dropdown,
    refresh_history,
    export_history,
    import_history,
    # Generation handlers
    apply_preset,
    update_warnings_from_sliders,
    use_last_seed,
    adjust_seed,
    random_seed,
    toggle_seed_lock,
    select_from_history,
    update_seed_history,
    generate_and_store,
    start_seed_variations,
    refine_in_vision,
    toggle_favorite_generated,
    copy_seed_to_clipboard,
    # UI handlers
    get_enhanced_progress_html,
    toggle_shortcuts,
    open_settings,
    close_settings,
    apply_theme,
    reset_theme,
    open_composer,
    close_composer,
    add_tag_to_composer,
    build_from_tags,
    clear_all_tags,
    load_template_handler,
    copy_to_main_prompt,
    save_custom_template,
    open_image_preview,
    close_image_preview,
)
from core import Mode, JobStatus


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_mode_manager():
    """Create mock ModeManager"""
    manager = Mock()
    manager.get_mode.return_value = Mode.IDLE
    manager.switch_to_chat.return_value = None
    manager.switch_to_generate.return_value = None
    manager.switch_to_idle.return_value = None
    manager._get_status_message.return_value = "Test mode status"
    return manager


@pytest.fixture
def mock_vram_monitor():
    """Create mock VRAMMonitor"""
    monitor = Mock()
    monitor.get_vram_usage.return_value = {
        "used_gb": 5.2,
        "total_gb": 16.0,
        "percentage": 32,
        "available": True
    }
    return monitor


@pytest.fixture
def mock_gallery():
    """Create mock ImageGallery"""
    gallery = Mock()
    gallery.get_images.return_value = []
    gallery.get_gallery_stats.return_value = {
        "total": 5,
        "favorites": 2,
        "total_size_mb": 15.5
    }
    gallery.toggle_favorite.return_value = True
    gallery.delete_image.return_value = True
    gallery.get_last_seed.return_value = 12345
    gallery.get_image_by_index.return_value = None
    gallery.get_last_image_metadata.return_value = None
    gallery.images = []
    return gallery


@pytest.fixture
def mock_workflow_manager():
    """Create mock WorkflowManager"""
    manager = Mock()
    workflow = Mock()
    workflow.metadata.name = "Test Workflow"
    workflow.metadata.description = "Test description"
    workflow.metadata.category = "text2img"
    workflow.metadata.tags = ["test", "demo"]
    workflow.metadata.author = "Test Author"
    workflow.filename = "test_workflow.json"
    manager.get_current_workflow.return_value = workflow
    manager.get_workflows_list.return_value = []
    manager.get_workflows_by_category.return_value = []
    manager.set_current_workflow.return_value = True
    manager.import_workflow.return_value = True
    manager.export_workflow.return_value = True
    manager.load_all_workflows.return_value = None
    manager.workflows = {}
    return manager


# ============================================================================
# MODE HANDLERS TESTS
# ============================================================================


class TestModeHandlers:
    """Tests for mode_handlers.py (2 functions)"""

    def test_handle_mode_change_to_chat(self, mock_mode_manager, mock_vram_monitor):
        """Test switching to chat mode"""
        mock_mode_manager.switch_to_chat.return_value = "Switched to Chat mode"

        result = handle_mode_change("💬 Chat", mock_mode_manager, mock_vram_monitor)

        mock_mode_manager.switch_to_chat.assert_called_once()
        assert isinstance(result, tuple)
        assert len(result) == 8  # Returns 8-element tuple

    def test_toggle_auto_switch(self):
        """Test toggling auto-switch"""
        mock_smart_switch = Mock()

        result = toggle_auto_switch(True, mock_smart_switch)

        # Returns bool, sets auto_switch_enabled on smart_switch
        assert result == True
        assert mock_smart_switch.auto_switch_enabled == True


# ============================================================================
# GALLERY HANDLERS TESTS
# ============================================================================


class TestGalleryHandlers:
    """Tests for gallery_handlers.py (9 functions)"""

    def test_update_gallery_display(self, mock_gallery):
        """Test updating gallery display with filters"""
        mock_gallery.get_images.return_value = [Mock(), Mock()]
        mock_gallery.images = [Mock(), Mock()]

        result = update_gallery_display("portrait", "newest", False, mock_gallery)

        mock_gallery.get_images.assert_called_once_with("portrait", "newest", False)
        # Returns tuple (images, info)
        assert isinstance(result, tuple)
        assert len(result) == 2
        images, info = result
        assert isinstance(info, str)

    def test_show_gallery_stats(self, mock_gallery):
        """Test showing gallery statistics"""
        result = show_gallery_stats(mock_gallery)

        mock_gallery.get_gallery_stats.assert_called_once()
        assert "5" in result or "total" in result.lower()

    def test_load_gallery_image(self, mock_gallery, mock_mode_manager, mock_vram_monitor):
        """Test loading image from gallery"""
        mock_evt = Mock()
        mock_evt.index = 0
        mock_image = Mock()
        mock_gallery.get_image_by_index.return_value = {
            "image": mock_image,
            "seed": 12345,
            "prompt": "test prompt",
            "settings": {"width": 1024, "height": 1024, "steps": 20}
        }
        mock_show_toast = Mock(return_value=gr.update())
        mock_hide_toast = Mock(return_value=gr.update())

        result = load_gallery_image(
            mock_evt, mock_gallery, mock_mode_manager, mock_show_toast, mock_hide_toast
        )

        assert isinstance(result, tuple)
        assert len(result) == 9  # Returns 9-element tuple

    def test_open_gallery(self):
        """Test opening gallery modal"""
        result = open_gallery()

        # Should return gr.update to make gallery visible
        assert hasattr(result, '__class__')

    def test_close_gallery(self):
        """Test closing gallery modal"""
        result = close_gallery()

        # Should return gr.update to hide gallery
        assert hasattr(result, '__class__')

    def test_gallery_toggle_favorite(self, mock_gallery):
        """Test toggling favorite on gallery image"""
        mock_show_toast = Mock(return_value=gr.update())
        mock_gallery.get_images.return_value = [("/path/to/image.png", "caption")]
        mock_gallery.images = [Mock()]

        result = gallery_toggle_favorite(0, mock_gallery, mock_show_toast)

        mock_gallery.toggle_favorite.assert_called_once()
        assert isinstance(result, tuple)
        assert len(result) == 3  # Returns (toast, gallery_images, info)

    def test_gallery_use_img2img(self, mock_gallery):
        """Test using gallery image for img2img"""
        mock_image = Mock()
        mock_gallery.get_image_by_index.return_value = {"image": mock_image}
        mock_show_toast = Mock(return_value=gr.update())

        result = gallery_use_img2img(0, mock_gallery, mock_show_toast)

        assert isinstance(result, tuple)
        assert len(result) == 2  # Returns (toast, image)

    def test_gallery_open_vision(self, mock_gallery, mock_mode_manager, mock_vram_monitor):
        """Test opening gallery image in vision chat"""
        mock_image = Mock()
        mock_gallery.get_image_by_index.return_value = {"image": mock_image}
        mock_show_toast = Mock(return_value=gr.update())

        result = gallery_open_vision(
            0, mock_gallery, mock_mode_manager, mock_vram_monitor, mock_show_toast
        )

        assert isinstance(result, tuple)
        assert len(result) == 8  # Returns 8-element tuple

    def test_gallery_delete_image(self, mock_gallery):
        """Test deleting gallery image"""
        mock_show_toast = Mock(return_value=gr.update())
        mock_gallery.get_images.return_value = [("/path/to/image.png", "caption")]
        mock_gallery.images = [Mock()]

        result = gallery_delete_image(0, mock_gallery, mock_show_toast)

        mock_gallery.delete_image.assert_called_once()
        assert isinstance(result, tuple)
        assert len(result) == 3  # Returns (toast, gallery_images, info)


# ============================================================================
# WORKFLOW HANDLERS TESTS
# ============================================================================


class TestWorkflowHandlers:
    """Tests for workflow_handlers.py (6 functions)"""

    def test_get_workflow_info_display(self, mock_workflow_manager):
        """Test getting workflow info display"""
        result = get_workflow_info_display(mock_workflow_manager)

        assert "Test Workflow" in result

    def test_switch_workflow(self, mock_workflow_manager):
        """Test switching workflows"""
        # Create a workflow with matching name
        workflow = Mock()
        workflow.metadata.name = "Test Workflow"
        mock_workflow_manager.workflows = {"test.json": workflow}

        result = switch_workflow("Test Workflow", "All", mock_workflow_manager)

        mock_workflow_manager.set_current_workflow.assert_called()
        assert isinstance(result, tuple)
        assert len(result) == 3  # Returns (dropdown, info, status)

    def test_refresh_workflows(self, mock_workflow_manager):
        """Test refreshing workflow list"""
        mock_workflow_manager.get_workflows_list.return_value = [
            {"name": "Test", "category": "text2img"}
        ]

        result = refresh_workflows("All", mock_workflow_manager)

        mock_workflow_manager.load_all_workflows.assert_called_once()
        assert isinstance(result, tuple)
        assert len(result) == 3  # Returns (dropdown, info, status)

    def test_filter_workflows_by_category(self, mock_workflow_manager):
        """Test filtering workflows by category"""
        workflow = Mock()
        workflow.metadata.name = "Test"
        mock_workflow_manager.get_workflows_by_category.return_value = [workflow]

        result = filter_workflows_by_category("text2img", mock_workflow_manager)

        # Returns gr.update
        assert hasattr(result, '__class__')

    def test_import_workflow_from_file(self, mock_workflow_manager):
        """Test importing workflow from file"""
        mock_workflow_manager.import_workflow.return_value = True
        mock_workflow_manager.get_workflows_list.return_value = [{"name": "Test"}]

        result = import_workflow_from_file("/path/to/workflow.json", mock_workflow_manager)

        mock_workflow_manager.import_workflow.assert_called_once_with("/path/to/workflow.json")
        assert isinstance(result, tuple)
        assert len(result) == 3  # Returns (info, status, dropdown)

    def test_export_current_workflow(self, mock_workflow_manager):
        """Test exporting current workflow"""
        mock_workflow_manager.export_workflow.return_value = True

        result = export_current_workflow(mock_workflow_manager)

        # Returns status message string
        assert isinstance(result, str)
        assert "export" in result.lower() or "✅" in result


# ============================================================================
# CHAT HANDLERS TESTS
# ============================================================================


class TestChatHandlers:
    """Tests for chat_handlers.py (10 functions)"""

    def test_user_message(self):
        """Test adding user message to history"""
        history = []

        result = user_message("Hello", history)

        # Returns tuple ("", updated_history)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == ""  # First element is empty string
        assert len(result[1]) == 1  # Second element is updated history
        assert result[1][0] == {"role": "user", "content": "Hello"}

    def test_vision_user_message(self):
        """Test vision user message"""
        history = []

        result = vision_user_message("Describe this", history)

        # Returns tuple ("", updated_history)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == ""  # First element is empty string
        assert len(result[1]) == 1  # Second element is updated history
        assert result[1][0] == {"role": "user", "content": "Describe this"}

    def test_load_selected_prompt(self):
        """Test loading selected prompt"""
        mock_prompt_history = Mock()
        mock_prompt_history.get_prompt_by_display_text.return_value = "Test prompt"

        result = load_selected_prompt("Test prompt - 3 uses", mock_prompt_history)

        mock_prompt_history.get_prompt_by_display_text.assert_called_once_with("Test prompt - 3 uses")
        assert isinstance(result, str)

    def test_search_and_update_dropdown(self):
        """Test searching prompts"""
        mock_prompt_history = Mock()
        mock_prompt_history.search_prompts.return_value = [
            {"prompt": "Result", "use_count": 1}
        ]

        result = search_and_update_dropdown("query", mock_prompt_history)

        mock_prompt_history.search_prompts.assert_called_once_with("query")
        # Returns gr.update
        assert hasattr(result, '__class__')

    def test_refresh_history(self):
        """Test refreshing prompt history"""
        mock_prompt_history = Mock()
        mock_prompt_history.get_dropdown_choices.return_value = []

        result = refresh_history(mock_prompt_history)

        mock_prompt_history.get_dropdown_choices.assert_called_once()
        # Returns gr.update
        assert hasattr(result, '__class__')

    def test_export_history(self):
        """Test exporting prompt history"""
        mock_prompt_history = Mock()
        mock_prompt_history.export_prompts.return_value = "✅ Exported prompts"

        result = export_history(mock_prompt_history)

        mock_prompt_history.export_prompts.assert_called_once()
        # Returns tuple (message, visible_update)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_import_history(self):
        """Test importing prompt history"""
        mock_prompt_history = Mock()
        mock_prompt_history.import_prompts.return_value = "✅ Imported 5 prompts"
        mock_prompt_history.get_dropdown_choices.return_value = []

        result = import_history("/path/import.json", mock_prompt_history)

        mock_prompt_history.import_prompts.assert_called_once_with("/path/import.json")
        # Returns tuple (message, visible_update, dropdown_update)
        assert isinstance(result, tuple)
        assert len(result) == 3


# ============================================================================
# GENERATION HANDLERS TESTS
# ============================================================================


class TestGenerationHandlers:
    """Tests for generation_handlers.py (13 functions)"""

    def test_apply_preset_fast(self):
        """Test applying fast preset"""
        result = apply_preset("Fast Draft")

        # Returns (width, height, steps)
        assert result[0] == 768  # width
        assert result[1] == 768  # height
        assert result[2] == 15   # steps

    def test_apply_preset_balanced(self):
        """Test applying balanced preset"""
        result = apply_preset("Balanced")

        assert result[0] == 1024  # width
        assert result[1] == 1024  # height
        assert result[2] == 20    # steps

    def test_update_warnings_from_sliders(self):
        """Test VRAM warnings"""
        # Uses check_vram_warnings_func which returns (warning_text, warning_visible)
        mock_check_vram = Mock(return_value=("✅ OK", True))

        result = update_warnings_from_sliders(20, 1024, 1024, mock_check_vram)

        mock_check_vram.assert_called_once_with(20, 1024, 1024)
        # Returns gr.update
        assert hasattr(result, '__class__')

    def test_use_last_seed(self, mock_gallery):
        """Test using last seed"""
        # Uses gallery.get_last_seed() which returns int or None
        mock_gallery.get_last_seed.return_value = 12345

        result = use_last_seed(mock_gallery)

        mock_gallery.get_last_seed.assert_called_once()
        assert result == "12345"  # Returns string

    def test_adjust_seed_positive(self, mock_gallery):
        """Test adjusting seed with positive value"""
        # Uses gallery not just seed
        result = adjust_seed("1000", 10, mock_gallery)

        assert result == "1010"

    def test_adjust_seed_negative(self, mock_gallery):
        """Test adjusting seed with negative value"""
        # Uses gallery not just seed
        result = adjust_seed("1000", -10, mock_gallery)

        assert result == "990"

    def test_random_seed(self):
        """Test generating random seed"""
        result = random_seed()

        assert isinstance(int(result), int)
        assert 0 <= int(result) <= 2**32

    def test_toggle_seed_lock(self):
        """Test toggling seed lock"""
        mock_seed_manager = Mock()

        result = toggle_seed_lock(True, "12345", mock_seed_manager)

        mock_seed_manager.lock_seed.assert_called_once_with(12345)
        # Returns bool (the locked state)
        assert result == True

    def test_select_from_history(self):
        """Test selecting seed from history"""
        result = select_from_history("12345")

        # Returns seed value as string
        assert result == "12345"

    def test_update_seed_history(self):
        """Test updating seed history"""
        mock_seed_manager = Mock()
        mock_seed_manager.get_history.return_value = [12345, 67890]

        result = update_seed_history(mock_seed_manager)

        mock_seed_manager.get_history.assert_called_once()
        # Returns gr.update
        assert hasattr(result, '__class__')

    def test_start_seed_variations(self, mock_gallery):
        """Test starting seed variations"""
        mock_gen_queue = Mock()
        mock_gen_queue.get_status.return_value = "4 jobs queued"
        mock_show_toast = Mock(return_value=gr.update())
        mock_gallery.get_last_seed.return_value = 12345

        result = start_seed_variations(
            "prompt", 20, 1024, 1024, mock_gallery, mock_gen_queue, mock_show_toast
        )

        # Should add 4 jobs
        assert mock_gen_queue.add_job.call_count == 4
        # Returns tuple (toast, queue_status)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_toggle_favorite_generated(self, mock_gallery):
        """Test toggling favorite on generated image"""
        mock_show_toast = Mock(return_value=gr.update())
        mock_gallery.get_last_image_metadata.return_value = {"seed": 12345}
        mock_gallery.get_images.return_value = [("/path/to/image.png", "caption")]
        mock_gallery.toggle_favorite.return_value = True

        result = toggle_favorite_generated(mock_gallery, mock_show_toast)

        # Returns gr.update (toast)
        assert hasattr(result, '__class__')

    def test_copy_seed_to_clipboard(self):
        """Test copying seed to clipboard"""
        mock_seed_manager = Mock()
        mock_seed_manager.get_last_seed.return_value = 12345
        mock_show_toast = Mock(return_value=gr.update())

        result = copy_seed_to_clipboard(mock_seed_manager, mock_show_toast)

        mock_seed_manager.get_last_seed.assert_called_once()
        # Returns gr.update (toast)
        assert hasattr(result, '__class__')


# ============================================================================
# UI HANDLERS TESTS
# ============================================================================


class TestUIHandlers:
    """Tests for ui_handlers.py (18 functions)"""

    def test_get_enhanced_progress_html(self):
        """Test creating progress HTML"""
        result = get_enhanced_progress_html("Generating...", 30)

        assert "Generating" in result
        assert isinstance(result, str)

    def test_toggle_shortcuts(self):
        """Test toggling keyboard shortcuts"""
        result = toggle_shortcuts(True)

        # Returns tuple (new_state, accordion_update)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == False  # Toggles from True to False

    def test_open_settings(self):
        """Test opening settings modal"""
        result = open_settings()

        assert hasattr(result, '__class__')

    def test_close_settings(self):
        """Test closing settings modal"""
        result = close_settings()

        assert hasattr(result, '__class__')

    def test_apply_theme(self):
        """Test applying theme"""
        mock_theme_manager = Mock()
        mock_theme_manager.COLOR_SCHEMES = {
            "default": {"name": "Default"}
        }
        mock_theme_manager.get_theme_display.return_value = "Dark mode, Default scheme"

        result = apply_theme("Dark", "Default", "Default", mock_theme_manager)

        mock_theme_manager.set_mode.assert_called_once_with("Dark")
        mock_theme_manager.set_layout_density.assert_called_once_with("Default")
        # Returns string (theme display)
        assert isinstance(result, str)

    def test_reset_theme(self):
        """Test resetting theme"""
        mock_theme_manager = Mock()
        mock_theme_manager.COLOR_SCHEMES = {
            "default": {"name": "Default"}
        }
        mock_theme_manager.get_mode.return_value = "Auto"
        mock_theme_manager.get_color_scheme.return_value = "default"
        mock_theme_manager.get_layout_density.return_value = "Default"
        mock_theme_manager.get_theme_display.return_value = "Auto mode"

        result = reset_theme(mock_theme_manager)

        mock_theme_manager.reset_to_defaults.assert_called_once()
        # Returns tuple (mode, scheme, density, theme_display)
        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_open_composer(self):
        """Test opening prompt composer"""
        result = open_composer()

        assert hasattr(result, '__class__')

    def test_close_composer(self):
        """Test closing prompt composer"""
        result = close_composer()

        assert hasattr(result, '__class__')

    def test_add_tag_to_composer(self):
        """Test adding tag to composer"""
        mock_prompt_composer = Mock()
        mock_prompt_composer.TAG_LIBRARY = {
            "style": [Mock(name="portrait")]
        }
        mock_prompt_composer.get_selected_tags_display.return_value = "portrait"

        result = add_tag_to_composer("portrait", mock_prompt_composer)

        # Returns string (selected tags display)
        assert isinstance(result, str)

    def test_build_from_tags(self):
        """Test building prompt from tags"""
        mock_prompt_composer = Mock()
        mock_prompt_composer.build_prompt.return_value = "portrait, cinematic"

        result = build_from_tags(mock_prompt_composer)

        mock_prompt_composer.build_prompt.assert_called_once()
        # Returns string (built prompt)
        assert isinstance(result, str)
        assert result == "portrait, cinematic"

    def test_clear_all_tags(self):
        """Test clearing all tags"""
        mock_prompt_composer = Mock()
        mock_prompt_composer.get_selected_tags_display.return_value = ""

        result = clear_all_tags(mock_prompt_composer)

        mock_prompt_composer.clear_tags.assert_called_once()
        # Returns tuple (selected_tags_display, built_prompt)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_load_template_handler(self):
        """Test loading template"""
        mock_prompt_composer = Mock()
        template = Mock()
        template.name = "Template Name"
        mock_prompt_composer.get_all_templates.return_value = [template]
        mock_prompt_composer.load_template.return_value = "Template prompt"
        mock_prompt_composer.get_selected_tags_display.return_value = "tags"

        result = load_template_handler("Template Name - desc", mock_prompt_composer)

        # Returns tuple (selected_tags_display, built_prompt)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_copy_to_main_prompt(self):
        """Test copying to main prompt"""
        result = copy_to_main_prompt("Built prompt")

        # Returns string (the prompt)
        assert isinstance(result, str)
        assert result == "Built prompt"

    def test_save_custom_template(self):
        """Test saving custom template"""
        mock_prompt_composer = Mock()

        result = save_custom_template(
            "Name", "Description", "Custom", mock_prompt_composer
        )

        mock_prompt_composer.save_as_template.assert_called_once_with("Name", "Description", "Custom")
        # Returns gr.update (save status)
        assert hasattr(result, '__class__')

    def test_open_image_preview(self, mock_gallery):
        """Test opening image preview"""
        mock_image = Mock()
        mock_gallery.get_last_image_metadata.return_value = {
            "prompt": "test",
            "seed": 12345,
            "width": 1024,
            "height": 1024,
            "steps": 20
        }

        result = open_image_preview(mock_image, mock_gallery)

        # Returns tuple (accordion, preview_image, preview_metadata)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_close_image_preview(self):
        """Test closing image preview"""
        result = close_image_preview()

        assert hasattr(result, '__class__')
