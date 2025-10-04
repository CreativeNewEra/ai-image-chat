"""Unit tests for the workflow manager module without interactive output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import app
from core import Mode, WorkflowManager


@pytest.fixture
def populated_workflows_dir(tmp_path: Path) -> Path:
    categories = [
        ("text2img", "Text2Image", "Portrait Workflow"),
        ("img2img", "Image2Image", "Upscale Workflow"),
    ]

    for index, (folder, category, name) in enumerate(categories):
        category_dir = tmp_path / folder
        category_dir.mkdir(parents=True)

        workflow_file = category_dir / f"workflow_{index}.json"
        workflow_file.write_text(json.dumps({"nodes": [{"id": index}]}), encoding="utf-8")

        metadata = {
            "name": name,
            "description": f"Sample {category} workflow",
            "category": category,
            "tags": ["sample"],
        }
        meta_file = category_dir / f"workflow_{index}_meta.json"
        meta_file.write_text(json.dumps(metadata), encoding="utf-8")

    return tmp_path


@pytest.fixture
def workflows_with_duplicate_names(tmp_path: Path) -> Path:
    """Create workflows that share the same filename in different folders."""

    configs = [
        ("folder_one", "Shared Workflow A", "General"),
        ("folder_two", "Shared Workflow B", "Custom"),
    ]

    for folder, name, category in configs:
        target_dir = tmp_path / folder
        target_dir.mkdir(parents=True)

        data = {"nodes": [{"id": name}]}
        workflow_file = target_dir / "shared.json"
        workflow_file.write_text(json.dumps(data), encoding="utf-8")

        metadata = {
            "name": name,
            "description": f"Workflow for {name}",
            "category": category,
            "tags": ["duplicate"],
        }
        meta_file = target_dir / "shared_meta.json"
        meta_file.write_text(json.dumps(metadata), encoding="utf-8")

    return tmp_path


def test_workflow_manager_lists_categories_and_search(populated_workflows_dir: Path) -> None:
    manager = WorkflowManager(str(populated_workflows_dir))

    assert manager.get_workflow_count() == 2

    categories = manager.get_all_categories()
    assert categories == ["Image2Image", "Text2Image"]

    results = manager.search_workflows("portrait")
    assert len(results) == 1
    assert results[0].metadata.name == "Portrait Workflow"


def test_workflow_manager_delete_removes_files(populated_workflows_dir: Path) -> None:
    manager = WorkflowManager(str(populated_workflows_dir))

    filename = "workflow_0.json"
    workflow_path = populated_workflows_dir / "text2img" / filename
    metadata_path = populated_workflows_dir / "text2img" / "workflow_0_meta.json"

    assert workflow_path.exists()
    assert metadata_path.exists()

    assert manager.delete_workflow(filename) is True
    assert manager.get_workflow(filename) is None
    assert not workflow_path.exists()
    assert not metadata_path.exists()
    assert manager.get_workflow_count() == 1


def test_workflow_manager_handles_duplicate_filenames(
    workflows_with_duplicate_names: Path,
) -> None:
    manager = WorkflowManager(str(workflows_with_duplicate_names))

    assert manager.get_workflow_count() == 2

    paths = {entry["path"] for entry in manager.get_workflows_list()}
    assert paths == {"folder_one/shared.json", "folder_two/shared.json"}

    first = manager.get_workflow("folder_one/shared.json")
    assert first is not None
    assert first.metadata.name == "Shared Workflow A"

    # Ambiguous lookup by filename should fail
    assert manager.get_workflow("shared.json") is None

    assert manager.set_current_workflow("folder_two/shared.json") is True
    assert manager.get_current_workflow() is not None
    assert manager.get_current_workflow().metadata.name == "Shared Workflow B"

    assert manager.delete_workflow("folder_one/shared.json") is True
    assert manager.get_workflow_count() == 1
    assert manager.get_workflow("folder_two/shared.json") is not None


def test_generate_image_accepts_text2image_category(
    populated_workflows_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Workflows with title case categories should match slug comparisons."""

    manager = WorkflowManager(str(populated_workflows_dir))
    manager.current_workflow_name = None

    monkeypatch.setattr(app, "workflow_manager", manager)
    monkeypatch.setattr(app.mode_manager, "get_mode", lambda: Mode.GENERATE)
    monkeypatch.setattr(app.comfy, "load_workflow_from_data", lambda data: True)
    monkeypatch.setattr(app.gallery, "add_image", lambda *_, **__: None)
    monkeypatch.setattr(app.session_stats, "add_generation", lambda *_: None)
    monkeypatch.setattr(app.session_stats, "get_stats_display", lambda: "stats")
    monkeypatch.setattr(app.seed_manager, "add_seed", lambda *_: None)
    monkeypatch.setattr(app.prompt_history, "add_prompt", lambda *_, **__: None)

    def fake_get_seed(seed):
        return 42

    monkeypatch.setattr(app.seed_manager, "get_seed_for_generation", fake_get_seed)

    def fake_generate_image(**kwargs):
        return "image-bytes", "success", kwargs["seed"]

    monkeypatch.setattr(app.comfy, "generate_image", fake_generate_image)

    image, status, actual_seed, _ = app.generate_image(
        prompt_text="Prompt long enough",
        steps=10,
        width=768,
        height=768,
        seed_value="",
    )

    assert image == "image-bytes"
    assert "No text2img workflow available" not in status
    assert actual_seed == 42
    current = manager.get_current_workflow()
    assert current is not None
    assert current.metadata.matches_category("text2img")
