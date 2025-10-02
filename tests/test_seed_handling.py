"""Unit tests for seed parsing and fallback behavior in app functions."""

import logging

import pytest

import app
from core.mode_manager import Mode


@pytest.fixture(autouse=True)
def ensure_generate_mode(monkeypatch):
    """Ensure tests run with generation mode active."""
    monkeypatch.setattr(app.mode_manager, "get_mode", lambda: Mode.GENERATE)


@pytest.fixture(autouse=True)
def stub_workflow_loading(monkeypatch):
    """Avoid heavy workflow loading by stubbing the comfy bridge."""
    monkeypatch.setattr(app.workflow_manager, "get_current_workflow", lambda: None)
    monkeypatch.setattr(app.comfy, "load_workflow", lambda: True)
    monkeypatch.setattr(app.comfy, "load_workflow_from_data", lambda data: True)


@pytest.fixture(autouse=True)
def stub_generation_dependencies(monkeypatch):
    """Stub objects touched during generation to keep tests fast and isolated."""
    monkeypatch.setattr(app.gallery, "add_image", lambda *_, **__: None)
    monkeypatch.setattr(app.session_stats, "add_generation", lambda *_: None)
    monkeypatch.setattr(app.session_stats, "get_stats_display", lambda: "stats")
    monkeypatch.setattr(app.seed_manager, "add_seed", lambda *_: None)
    monkeypatch.setattr(app.prompt_history, "add_prompt", lambda *_, **__: None)


def test_generate_image_valid_seed(monkeypatch):
    captured = {}

    def fake_get_seed_for_generation(seed):
        captured["seed"] = seed
        return seed

    monkeypatch.setattr(app.seed_manager, "get_seed_for_generation", fake_get_seed_for_generation)

    def fake_generate_image(**kwargs):
        captured["used_seed"] = kwargs["seed"]
        return "image-bytes", "ok", kwargs["seed"]

    monkeypatch.setattr(app.comfy, "generate_image", fake_generate_image)

    image, status, actual_seed, _ = app.generate_image(
        prompt_text="Prompt long enough",
        steps=10,
        width=768,
        height=768,
        seed_value="123",
    )

    assert captured["seed"] == 123
    assert captured["used_seed"] == 123
    assert actual_seed == 123
    assert image == "image-bytes"
    assert "ok" in status.lower()


def test_generate_image_invalid_seed_logs_and_defaults(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    captured = {}

    def fake_get_seed_for_generation(seed):
        captured["seed"] = seed
        return 999  # pretend lock chooses deterministic seed

    monkeypatch.setattr(app.seed_manager, "get_seed_for_generation", fake_get_seed_for_generation)

    def fake_generate_image(**kwargs):
        captured["used_seed"] = kwargs["seed"]
        return None, "failed", 999

    monkeypatch.setattr(app.comfy, "generate_image", fake_generate_image)

    image, status, actual_seed, _ = app.generate_image(
        prompt_text="Prompt long enough",
        steps=10,
        width=768,
        height=768,
        seed_value="not-a-number",
    )

    assert captured["seed"] is None
    assert captured["used_seed"] == 999
    assert any("Invalid seed input" in record.message for record in caplog.records)
    assert actual_seed == 999
    assert image is None
    assert "failed" in status


def test_generate_image_blank_seed_uses_default(monkeypatch):
    captured = {}

    def fake_get_seed_for_generation(seed):
        captured["seed"] = seed
        return 321

    monkeypatch.setattr(app.seed_manager, "get_seed_for_generation", fake_get_seed_for_generation)

    def fake_generate_image(**kwargs):
        captured["used_seed"] = kwargs["seed"]
        return None, "failed", 321

    monkeypatch.setattr(app.comfy, "generate_image", fake_generate_image)

    app.generate_image(
        prompt_text="Prompt long enough",
        steps=10,
        width=768,
        height=768,
        seed_value="  ",
    )

    assert captured["seed"] is None
    assert captured["used_seed"] == 321


def test_add_to_queue_seed_parsing(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    captured = {}

    def fake_add_job(prompt, width, height, steps, seed):
        captured.setdefault("calls", []).append(seed)
        return "job-1"

    monkeypatch.setattr(app.gen_queue, "add_job", fake_add_job)
    monkeypatch.setattr(app.gen_queue, "get_queue_display", lambda: "display")

    # Valid seed
    app.add_to_queue("Prompt long enough", 10, 768, 768, "5")
    # Invalid seed falls back to random (-1)
    app.add_to_queue("Prompt long enough", 10, 768, 768, "oops")
    # Blank seed also uses random default (-1)
    app.add_to_queue("Prompt long enough", 10, 768, 768, "   ")

    assert captured["calls"] == [5, -1, -1]
    assert any("Invalid seed input" in record.message for record in caplog.records)


def test_add_batch_variations_seed_fallback(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    captured = {}

    def fake_add_batch(prompt, width, height, steps, seed, count):
        captured.setdefault("calls", []).append(seed)
        return [f"job-{i}" for i in range(count)]

    monkeypatch.setattr(app.gen_queue, "add_batch_variations", fake_add_batch)
    monkeypatch.setattr(app.gen_queue, "get_queue_display", lambda: "display")
    monkeypatch.setattr(app.seed_manager, "get_history", lambda: [111, 222])

    # Valid seed used directly
    app.add_batch_variations("Prompt long enough", 10, 768, 768, "7", count=3)
    # Invalid seed falls back to history
    app.add_batch_variations("Prompt long enough", 10, 768, 768, "bad", count=2)
    # Blank seed falls back to history
    app.add_batch_variations("Prompt long enough", 10, 768, 768, "  ", count=2)

    assert captured["calls"] == [7, 111, 111]
    assert any("Invalid seed input" in record.message for record in caplog.records)

