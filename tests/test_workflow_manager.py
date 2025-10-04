"""Unit tests for the workflow manager module without interactive output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import WorkflowManager


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
