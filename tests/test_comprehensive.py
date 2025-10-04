"""Comprehensive smoke tests for core modules with real assertions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

import config
from core import (
    GenerationQueue,
    ImageGallery,
    JobStatus,
    PromptHistory,
    SeedManager,
    SessionStats,
    WorkflowManager,
)


@pytest.fixture
def workflows_dir(tmp_path: Path) -> Path:
    """Create a temporary workflows directory populated with a sample workflow."""
    text2img_dir = tmp_path / "text2img"
    text2img_dir.mkdir(parents=True)

    workflow_payload = {"nodes": [{"id": 1, "type": "TestNode"}]}
    workflow_file = text2img_dir / "sample.json"
    workflow_file.write_text(json.dumps(workflow_payload), encoding="utf-8")

    metadata = {
        "name": "Sample Workflow",
        "description": "Workflow loaded for unit testing",
        "category": "Text2Image",
        "tags": ["test"],
    }
    meta_file = text2img_dir / "sample_meta.json"
    meta_file.write_text(json.dumps(metadata), encoding="utf-8")

    return tmp_path


@pytest.fixture
def temp_output_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Patch the image output directory so tests do not touch real files."""
    monkeypatch.setattr(config, "OUTPUT_DIR", str(tmp_path))
    return tmp_path


def test_workflow_manager_loads_workflows(workflows_dir: Path) -> None:
    manager = WorkflowManager(str(workflows_dir))

    assert manager.get_workflow_count() == 1

    listing = manager.get_workflows_list()
    assert listing == [
        {
            "filename": "sample.json",
            "path": "text2img/sample.json",
            "name": "Sample Workflow",
            "category": "Text2Image",
            "description": "Workflow loaded for unit testing",
            "tags": ["test"],
        }
    ]

    assert manager.set_current_workflow("sample.json") is True
    current = manager.get_current_workflow()
    assert current is not None
    assert current.metadata.name == "Sample Workflow"

    stats = manager.get_stats()
    assert stats["total"] == 1
    assert stats["categories"] == {"Text2Image": 1}
    assert stats["current"] == "sample.json"


def test_generation_queue_adds_jobs_and_variations() -> None:
    queue = GenerationQueue()
    single_job_id = queue.add_job("prompt", 1024, 1024, 20, 12345)
    assert queue.get_job(single_job_id) is not None

    variation_ids = queue.add_batch_variations("prompt", 1024, 1024, 20, 50000, count=3)
    assert len(variation_ids) == 3
    assert [job.seed for job in queue.jobs][-3:] == [50000, 50001, 50002]

    next_job = queue.get_next_job()
    assert next_job is not None
    assert next_job.status == JobStatus.PENDING


def test_generation_queue_status_and_cleanup() -> None:
    queue = GenerationQueue()
    job_id = queue.add_job("prompt", 512, 512, 10, 101)
    current_job = queue.get_job(job_id)
    assert current_job is not None

    queue.current_job = current_job
    current_job.status = JobStatus.PROCESSING

    status = queue.get_queue_status()
    assert status["processing"] == 1
    assert status["current_job"] == current_job.to_dict()

    current_job.status = JobStatus.COMPLETED
    queue.clear_completed()
    assert queue.get_queue_status()["total"] == 0
    assert queue.current_job is None


def test_image_gallery_add_filter_and_sort(temp_output_dir: Path) -> None:
    gallery = ImageGallery()

    for i in range(3):
        img = Image.new("RGB", (100, 100), color=(i * 40, i * 40, i * 40))
        prompt = f"test prompt {i}" if i != 1 else "portrait test"
        settings = {"width": 512 + i * 128, "height": 512, "steps": 20}
        gallery.add_image(img, prompt, 1000 + i, settings)

    filtered = gallery.get_images(filter_text="portrait")
    assert len(filtered) == 1

    sorted_by_seed = gallery.get_images(sort_by="seed")
    seeds = [entry["seed"] for entry in sorted(gallery.images, key=lambda item: item["seed"])]
    sorted_seeds = [
        next(data["seed"] for data in gallery.images if data["image"] is image)
        for image in sorted_by_seed
    ]
    assert sorted_seeds == seeds

    gallery.toggle_favorite(0)
    assert gallery.get_favorites_count() == 1

    stats = gallery.get_gallery_stats()
    assert stats["total"] == 3
    assert stats["favorites"] == 1


def test_session_stats_reports_summary() -> None:
    stats = SessionStats()
    stats.add_generation(15.5)
    stats.add_generation(12.3)
    stats.add_generation(18.7)

    snapshot = stats.get_stats()
    assert snapshot["total_images"] == 3
    assert snapshot["avg_time"] == pytest.approx(15.5, rel=1e-3)
    assert snapshot["fastest"] == pytest.approx(12.3, rel=1e-3)
    assert snapshot["slowest"] == pytest.approx(18.7, rel=1e-3)

    display = stats.get_stats_display()
    assert "Generated: 3 images" in display
    assert "Average time: 15.5s" in display


def test_seed_manager_tracks_history_and_locking() -> None:
    manager = SeedManager()
    manager.add_seed(12345)
    manager.add_seed(67890)

    assert manager.get_history() == [67890, 12345]

    manager.lock_seed(11111)
    assert manager.is_locked is True
    assert manager.get_seed_for_generation(22222) == 11111

    manager.unlock_seed()
    assert manager.is_locked is False
    assert manager.get_seed_for_generation(33333) == 33333


def test_prompt_history_adds_and_searches(tmp_path: Path) -> None:
    history_file = tmp_path / "prompts.json"
    history = PromptHistory(history_file=str(history_file))

    history.add_prompt("A colorful landscape with dramatic lighting", {"steps": 20})
    history.add_prompt("Portrait of a traveler at sunset", {"steps": 25})

    recent = history.get_recent_prompts(2)
    assert len(recent) == 2
    assert recent[0]["prompt"].startswith("Portrait")

    results = history.search_prompts("landscape")
    assert len(results) == 1
    assert "landscape" in results[0]["prompt"].lower()
