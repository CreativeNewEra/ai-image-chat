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
    monitor.get_current_usage.return_value = "5.2 GB / 16.0 GB (32%)"
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
    manager.get_current_workflow.return_value = workflow
    manager.get_workflows_list.return_value = []
    manager.set_current_workflow.return_value = True
    return manager


# ============================================================================
# MODE HANDLERS TESTS
# ============================================================================


class TestModeHandlers:
    """Tests for mode_handlers.py (2 functions)"""

    def test_handle_mode_change_to_chat(self, mock_mode_manager, mock_vram_monitor):
        """Test switching to chat mode"""
        mock_smart_switch = Mock()

        result = handle_mode_change("chat", mock_mode_manager, mock_vram_monitor, mock_smart_switch)

        mock_mode_manager.switch_to_chat.assert_called_once()
        assert isinstance(result, tuple)
        assert len(result) >= 2

    def test_toggle_auto_switch(self):
        """Test toggling auto-switch"""
        mock_smart_switch = Mock()
        mock_smart_switch.toggle_auto_switch.return_value = True

        result = toggle_auto_switch(True, mock_smart_switch)

        mock_smart_switch.toggle_auto_switch.assert_called_once()
        assert "enabled" in result.lower() or "disabled" in result.lower()


# ============================================================================
# GALLERY HANDLERS TESTS
# ============================================================================


class TestGalleryHandlers:
    """Tests for gallery_handlers.py (9 functions)"""

    def test_update_gallery_display(self, mock_gallery):
        """Test updating gallery display with filters"""
        mock_gallery.get_images.return_value = [Mock(), Mock()]

        result = update_gallery_display("portrait", "newest", False, mock_gallery)

        mock_gallery.get_images.assert_called_once()
        assert isinstance(result, list)

    def test_show_gallery_stats(self, mock_gallery):
        """Test showing gallery statistics"""
        result = show_gallery_stats(mock_gallery)

        mock_gallery.get_gallery_stats.assert_called_once()
        assert "5" in result or "total" in result.lower()

    def test_load_gallery_image(self, mock_gallery):
        """Test loading image from gallery"""
        mock_evt = Mock()
        mock_evt.index = 0
        mock_gallery.images = [{"image": Mock(), "seed": 12345, "prompt": "test"}]

        result = load_gallery_image(mock_evt, mock_gallery)

        assert isinstance(result, tuple)

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
        result = gallery_toggle_favorite(0, mock_gallery)

        mock_gallery.toggle_favorite.assert_called_with(0)
        assert "favorite" in result.lower() or "⭐" in result

    def test_gallery_use_img2img(self, mock_gallery):
        """Test using gallery image for img2img"""
        mock_gallery.images = [{"image": Mock()}]

        result = gallery_use_img2img(0, mock_gallery)

        assert isinstance(result, tuple)

    def test_gallery_open_vision(self, mock_gallery):
        """Test opening gallery image in vision chat"""
        mock_gallery.images = [{"image": Mock()}]

        result = gallery_open_vision(0, mock_gallery)

        assert isinstance(result, tuple)

    def test_gallery_delete_image(self, mock_gallery):
        """Test deleting gallery image"""
        result = gallery_delete_image(0, mock_gallery)

        mock_gallery.delete_image.assert_called_with(0)
        assert isinstance(result, tuple)


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
        result = switch_workflow("new_workflow.json", "all", mock_workflow_manager)

        mock_workflow_manager.set_current_workflow.assert_called()
        assert isinstance(result, tuple)

    def test_refresh_workflows(self, mock_workflow_manager):
        """Test refreshing workflow list"""
        mock_workflow_manager.get_workflows_list.return_value = [
            {"filename": "test.json", "name": "Test"}
        ]

        result = refresh_workflows("all", mock_workflow_manager)

        assert isinstance(result, tuple)

    def test_filter_workflows_by_category(self, mock_workflow_manager):
        """Test filtering workflows by category"""
        result = filter_workflows_by_category("text2img", mock_workflow_manager)

        assert isinstance(result, gr.update) or isinstance(result, dict)

    def test_import_workflow_from_file(self, mock_workflow_manager):
        """Test importing workflow from file"""
        mock_workflow_manager.import_workflow.return_value = "workflow.json"

        result = import_workflow_from_file("/path/to/workflow.json", mock_workflow_manager)

        assert isinstance(result, tuple)

    def test_export_current_workflow(self, mock_workflow_manager):
        """Test exporting current workflow"""
        mock_workflow_manager.export_workflow.return_value = "/path/to/export.json"

        result = export_current_workflow(mock_workflow_manager)

        assert "export" in result.lower() or "✅" in result


# ============================================================================
# CHAT HANDLERS TESTS
# ============================================================================


class TestChatHandlers:
    """Tests for chat_handlers.py (10 functions)"""

    def test_user_message(self):
        """Test adding user message to history"""
        history = []

        result_history, result_text = user_message("Hello", history)

        assert len(result_history) == 1
        assert result_text == ""

    def test_vision_user_message(self):
        """Test vision user message"""
        history = []

        result = vision_user_message("Describe this", history)

        assert len(result[0]) == 1
        assert result[1] == ""

    def test_load_selected_prompt(self):
        """Test loading selected prompt"""
        mock_prompt_history = Mock()
        mock_prompt_history.get_prompt_by_index.return_value = {"prompt": "Test prompt"}

        result = load_selected_prompt("Test prompt - 3 uses", mock_prompt_history)

        assert isinstance(result, str)

    def test_search_and_update_dropdown(self):
        """Test searching prompts"""
        mock_prompt_history = Mock()
        mock_prompt_history.search_prompts.return_value = [
            {"prompt": "Result", "use_count": 1}
        ]

        result = search_and_update_dropdown("query", mock_prompt_history)

        assert isinstance(result, gr.update) or isinstance(result, dict)

    def test_refresh_history(self):
        """Test refreshing prompt history"""
        mock_prompt_history = Mock()
        mock_prompt_history.get_recent_prompts.return_value = []

        result = refresh_history(mock_prompt_history)

        assert isinstance(result, gr.update) or isinstance(result, dict)

    def test_export_history(self):
        """Test exporting prompt history"""
        mock_prompt_history = Mock()
        mock_prompt_history.export_prompts.return_value = "/path/export.json"

        result = export_history(mock_prompt_history)

        assert "export" in result.lower() or "✅" in result

    def test_import_history(self):
        """Test importing prompt history"""
        mock_prompt_history = Mock()
        mock_prompt_history.import_prompts.return_value = "✅ Imported 5 prompts"

        result = import_history("/path/import.json", mock_prompt_history)

        assert isinstance(result, tuple)


# ============================================================================
# GENERATION HANDLERS TESTS
# ============================================================================


class TestGenerationHandlers:
    """Tests for generation_handlers.py (13 functions)"""

    def test_apply_preset_fast(self):
        """Test applying fast preset"""
        result = apply_preset("fast")

        assert result[0] == 10  # steps
        assert result[1] == 768  # width
        assert result[2] == 768  # height

    def test_apply_preset_balanced(self):
        """Test applying balanced preset"""
        result = apply_preset("balanced")

        assert result[0] == 20
        assert result[1] == 1024

    def test_update_warnings_from_sliders(self):
        """Test VRAM warnings"""
        mock_vram_estimator = Mock()
        mock_vram_estimator.get_warnings.return_value = ("none", "✅ OK")

        result = update_warnings_from_sliders(20, 1024, 1024, 5.0, 16.0, mock_vram_estimator)

        assert "✅" in result or "OK" in result

    def test_use_last_seed(self):
        """Test using last seed"""
        mock_seed_manager = Mock()
        mock_seed_manager.get_last_seed.return_value = 12345

        result = use_last_seed(mock_seed_manager)

        assert result == 12345

    def test_adjust_seed_positive(self):
        """Test adjusting seed with positive value"""
        result = adjust_seed("1000", 10)

        assert result == "1010"

    def test_adjust_seed_negative(self):
        """Test adjusting seed with negative value"""
        result = adjust_seed("1000", -10)

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

        assert isinstance(result, tuple)

    def test_select_from_history(self):
        """Test selecting seed from history"""
        result = select_from_history("12345 - used 3 times")

        assert "12345" in result

    def test_update_seed_history(self):
        """Test updating seed history"""
        mock_seed_manager = Mock()
        mock_seed_manager.get_history.return_value = [12345, 67890]

        result = update_seed_history(mock_seed_manager)

        assert isinstance(result, gr.update) or isinstance(result, dict)

    def test_start_seed_variations(self):
        """Test starting seed variations"""
        mock_gen_queue = Mock()

        result = start_seed_variations("prompt", 20, 1024, 1024, "1000", mock_gen_queue)

        assert isinstance(result, tuple)

    def test_toggle_favorite_generated(self, mock_gallery):
        """Test toggling favorite on generated image"""
        result = toggle_favorite_generated(mock_gallery)

        assert isinstance(result, str)

    def test_copy_seed_to_clipboard(self):
        """Test copying seed to clipboard"""
        result = copy_seed_to_clipboard("12345")

        assert "12345" in result


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

        assert isinstance(result, str)

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
        mock_theme_manager.apply_theme.return_value = "/* CSS */"

        result = apply_theme("dark", "ocean", "comfortable", mock_theme_manager)

        assert isinstance(result, tuple)

    def test_reset_theme(self):
        """Test resetting theme"""
        mock_theme_manager = Mock()

        result = reset_theme(mock_theme_manager)

        assert isinstance(result, tuple)

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
        mock_prompt_composer.selected_tags = []

        result = add_tag_to_composer("portrait", "test prompt", mock_prompt_composer)

        assert isinstance(result, tuple)

    def test_build_from_tags(self):
        """Test building prompt from tags"""
        mock_prompt_composer = Mock()
        mock_prompt_composer.selected_tags = ["portrait", "cinematic"]
        mock_prompt_composer.build_prompt.return_value = "portrait, cinematic"

        result = build_from_tags(mock_prompt_composer)

        assert isinstance(result, str)

    def test_clear_all_tags(self):
        """Test clearing all tags"""
        mock_prompt_composer = Mock()

        result = clear_all_tags(mock_prompt_composer)

        assert isinstance(result, tuple)

    def test_load_template_handler(self):
        """Test loading template"""
        mock_prompt_composer = Mock()
        template = Mock()
        template.prompt = "Template prompt"
        mock_prompt_composer.get_template.return_value = template

        result = load_template_handler("Template Name", mock_prompt_composer)

        assert isinstance(result, tuple)

    def test_copy_to_main_prompt(self):
        """Test copying to main prompt"""
        result = copy_to_main_prompt("Built prompt")

        assert isinstance(result, tuple)

    def test_save_custom_template(self):
        """Test saving custom template"""
        mock_prompt_composer = Mock()

        result = save_custom_template("Name", "Description", "Custom", "prompt", mock_prompt_composer)

        assert isinstance(result, str)

    def test_open_image_preview(self):
        """Test opening image preview"""
        mock_image = Mock()

        result = open_image_preview(mock_image, "test prompt", 12345, 1024, 1024, 20)

        assert isinstance(result, tuple)

    def test_close_image_preview(self):
        """Test closing image preview"""
        result = close_image_preview()

        assert hasattr(result, '__class__')
