import pytest


@pytest.fixture(autouse=True)
def openrouter_models():
    """These tests exercise the real model list fetching (with mocked HTTP)."""
    yield None
