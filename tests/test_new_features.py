"""Tests for new Phase 2.5 features using real implementations."""

import json
from pathlib import Path

import pytest

from core.prompt_history import PromptHistory
from core.vram_estimator import VRAMEstimator


@pytest.mark.parametrize(
    "width,height,steps,expected",
    [
        (1024, 1024, 20, 8.0),
        (768, 768, 15, 4.3),
        (1536, 1536, 30, 19.8),
        (2048, 2048, 35, 36.8),
    ],
)
def test_estimate_vram_matches_reference(width, height, steps, expected):
    """Ensure VRAM estimation returns stable, expected values."""
    assert VRAMEstimator.estimate_vram(width, height, steps) == pytest.approx(expected)


@pytest.mark.parametrize(
    "width,height,steps,current_vram,total_vram,expected_level,expected_phrase",
    [
        (1024, 1024, 20, 0, 16, "none", "✅ Estimated VRAM"),
        (2048, 2048, 35, 0, 16, "error", "OUT OF VRAM"),
        (1536, 1536, 30, 10, 20, "error", "INSUFFICIENT VRAM"),
    ],
)
def test_vram_warning_levels(width, height, steps, current_vram, total_vram, expected_level, expected_phrase):
    level, message = VRAMEstimator.get_warnings(width, height, steps, current_vram, total_vram)
    assert level == expected_level
    assert expected_phrase in message


def create_history(tmp_path: Path) -> PromptHistory:
    history_file = tmp_path / "prompt_history.json"
    return PromptHistory(history_file=str(history_file))


def test_prompt_history_add_and_retrieve(tmp_path):
    history = create_history(tmp_path)

    prompt = "A beautiful sunset over mountains with vibrant orange and purple clouds"
    settings = {"width": 1024, "height": 1024, "steps": 20}
    history.add_prompt(prompt, settings)

    recent = history.get_recent_prompts(1)
    assert len(recent) == 1
    assert recent[0]["prompt"] == prompt
    assert recent[0]["settings"] == settings


def test_prompt_history_deduplicates_and_increments_use_count(tmp_path):
    history = create_history(tmp_path)

    prompt = "Cyberpunk city street at night with neon lights and rain reflections"
    history.add_prompt(prompt)
    history.add_prompt(prompt)

    recent = history.get_recent_prompts(1)
    assert len(history.prompts) == 1
    assert recent[0]["use_count"] == 2


def test_prompt_history_search(tmp_path):
    history = create_history(tmp_path)

    prompts = [
        "Portrait of a wise old wizard with a long white beard and magical staff",
        "A beautiful sunset over the ocean with palm trees",
        "Space explorer discovering ancient alien ruins on a distant planet",
    ]

    for prompt in prompts:
        history.add_prompt(prompt)

    results = history.search_prompts("sunset")
    assert len(results) == 1
    assert "sunset" in results[0]["prompt"].lower()


def test_prompt_history_persists_to_disk(tmp_path):
    history = create_history(tmp_path)

    prompt = "Vibrant watercolor painting of a bustling futuristic marketplace"
    settings = {"width": 768, "height": 512, "steps": 25}
    history.add_prompt(prompt, settings)

    history_file = Path(history.history_file)
    assert history_file.exists()

    with history_file.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    assert data["prompts"][0]["prompt"] == prompt
    assert data["prompts"][0]["settings"] == settings

    reloaded_history = PromptHistory(history_file=str(history_file))
    reloaded_prompts = reloaded_history.get_recent_prompts(1)
    assert len(reloaded_prompts) == 1
    assert reloaded_prompts[0]["prompt"] == prompt
    assert reloaded_prompts[0]["settings"] == settings


def test_prompt_history_import_reports_actual_added(tmp_path):
    history = create_history(tmp_path)

    existing_prompt = "Atmospheric concept art of a misty forest temple at dawn"
    history.add_prompt(existing_prompt)

    duplicate_prompt = "Highly detailed digital painting of a dragon soaring above mountains"

    import_data = {
        "prompts": [
            {"prompt": existing_prompt, "timestamp": "2024-01-01T00:00:00"},
            {"prompt": duplicate_prompt, "timestamp": "2024-01-02T00:00:00"},
            {"prompt": duplicate_prompt, "timestamp": "2024-01-03T00:00:00"},
        ]
    }

    import_file = tmp_path / "import_prompts.json"
    import_file.write_text(json.dumps(import_data), encoding="utf-8")

    message = history.import_prompts(str(import_file))

    assert "✅ Imported 1 prompt" in message
    assert "2 duplicates skipped" in message

    # Ensure the history reflects the actual number of new prompts reported
    recent_prompts = history.get_recent_prompts(10)
    imported_prompts = [entry["prompt"] for entry in recent_prompts]

    assert duplicate_prompt in imported_prompts
    assert imported_prompts.count(duplicate_prompt) == 1
