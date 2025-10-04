"""Focused tests covering the Phase 2.5 queue and gallery enhancements."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import config
from core import GenerationQueue, ImageGallery, JobStatus


@pytest.fixture
def generation_queue() -> GenerationQueue:
    queue = GenerationQueue()
    queue.add_job("primary prompt", 1024, 1024, 20, 12345)
    queue.add_batch_variations("batch prompt", 1024, 1024, 20, 50000, count=4)
    return queue


@pytest.fixture
def temp_output_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(config, "OUTPUT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def gallery(temp_output_dir: Path) -> ImageGallery:
    gallery = ImageGallery()
    for i in range(5):
        img = Image.new("RGB", (64, 64), color=(i * 30, i * 30, i * 30))
        prompt = "portrait image" if i % 2 else "landscape scene"
        gallery.add_image(img, prompt, 1000 + i, {"width": 512, "height": 512, "steps": 20})
    return gallery


def test_generation_queue_cancel_pending_job(generation_queue: GenerationQueue) -> None:
    pending_job = next(job for job in generation_queue.jobs if job.status == JobStatus.PENDING)

    assert generation_queue.cancel_job(pending_job.id) is True
    assert pending_job.status == JobStatus.CANCELLED


def test_generation_queue_clear_completed_removes_finished_jobs(generation_queue: GenerationQueue) -> None:
    current_job = generation_queue.jobs[0]
    generation_queue.current_job = current_job

    current_job.status = JobStatus.PROCESSING
    current_job.status = JobStatus.COMPLETED

    generation_queue.clear_completed()

    assert all(job.status != JobStatus.COMPLETED for job in generation_queue.jobs)
    assert generation_queue.current_job is None


def test_generation_queue_estimate_time_remaining_counts_processing(generation_queue: GenerationQueue) -> None:
    current_job = generation_queue.jobs[0]
    generation_queue.current_job = current_job
    current_job.status = JobStatus.PROCESSING

    estimate = generation_queue.estimate_time_remaining(avg_generation_time=10)
    assert estimate == "~50s remaining"


def test_image_gallery_filters_and_sorting(gallery: ImageGallery) -> None:
    portraits = gallery.get_images(filter_text="portrait")
    assert len(portraits) == 2

    sorted_by_resolution = gallery.get_images(sort_by="resolution")
    assert len(sorted_by_resolution) == len(gallery.images)

    seeds_in_order = [entry["seed"] for entry in gallery.images]
    sorted_seeds = [
        next(item["seed"] for item in gallery.images if item["image"] is image)
        for image in sorted_by_resolution
    ]
    assert sorted_seeds == seeds_in_order


def test_image_gallery_favorites_and_stats(gallery: ImageGallery) -> None:
    gallery.toggle_favorite(1)
    gallery.toggle_favorite(3)

    favorites_only = gallery.get_images(favorites_only=True)
    assert len(favorites_only) == 2
    assert gallery.get_favorites_count() == 2

    stats = gallery.get_gallery_stats()
    assert stats["total"] == 5
    assert stats["favorites"] == 2


def test_image_gallery_delete_selected_removes_files(gallery: ImageGallery) -> None:
    first_path = Path(gallery.images[0]["filepath"])
    metadata_path = first_path.with_suffix(".json")
    assert first_path.exists()
    assert metadata_path.exists()

    deleted = gallery.delete_selected([0, 1])
    assert deleted == 2
    assert not first_path.exists()
    assert not metadata_path.exists()
    assert len(gallery.images) == 3
