"""Tests for Ollama model discovery helpers."""

import types

import pytest
import requests

import app


def test_get_available_models_builds_tags_url(monkeypatch):
    """Ensure the tags endpoint is built without clobbering '/api' elsewhere."""

    captured = {}

    def fake_get(url, *args, **kwargs):
        captured["url"] = url
        response = types.SimpleNamespace()
        response.status_code = 200
        response.json = lambda: {"models": [{"name": "llama3"}, {"name": "mistral"}]}
        return response

    monkeypatch.setattr(app, "OLLAMA_API", "http://example.com/some/api/path/api")
    monkeypatch.setattr(app.requests, "get", fake_get)

    models = app.get_available_models()

    assert (
        captured["url"]
        == "http://example.com/some/api/path/api/tags"
    )
    assert models == ["llama3", "mistral"]


def test_get_available_models_returns_fallback_on_failure(monkeypatch):
    """Keep the existing fallback list when the tags request fails."""

    def fake_get_error(*args, **kwargs):
        raise requests.RequestException()

    monkeypatch.setattr(app, "OLLAMA_API", "http://example.com/api")
    monkeypatch.setattr(app.requests, "get", fake_get_error)

    models = app.get_available_models()

    assert models == [
        app.OLLAMA_CHAT_MODEL,
        "mistral:7b",
        "mistral-small3.2:latest",
    ]
