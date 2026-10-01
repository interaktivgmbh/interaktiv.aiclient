from fake_openrouter import FakeOpenRouter
from interaktiv.aiclient.interfaces import IAIClient
from interaktiv.aiclient.testing import ACCEPTANCE_TESTING
from interaktiv.aiclient.testing import FUNCTIONAL_TESTING
from interaktiv.aiclient.testing import INTEGRATION_TESTING
from plone import api
from pytest_plone import fixtures_factory
from unittest import mock
from zope.component import getUtility

import pytest


pytest_plugins = ["pytest_plone"]

MODEL = "google/gemini-2.5-flash-image"

MODELS = [
    {"id": MODEL, "name": "Google: Gemini 2.5 Flash Image"},
    {"id": "mistralai/mistral-small", "name": "Mistral: Mistral Small"},
]


globals().update(
    fixtures_factory((
        (ACCEPTANCE_TESTING, "acceptance"),
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture(scope="session")
def openrouter():
    server = FakeOpenRouter()
    yield server
    server.stop()


@pytest.fixture(autouse=True)
def openrouter_models():
    """Never fetch the model list from the real OpenRouter API."""
    with mock.patch(
        "interaktiv.aiclient.vocabularies.models.get_openrouter_models",
        return_value=MODELS,
    ) as patched:
        yield patched


@pytest.fixture(autouse=True)
def fresh_ai_client():
    """The client is a global utility: start every test uninitialised."""
    client = getUtility(IAIClient)
    client._client = None
    client._selected_model = None
    yield client
    client._client = None
    client._selected_model = None


@pytest.fixture
def ai_client(portal, openrouter, fresh_ai_client):
    """The AI client, configured against the fake OpenRouter server."""
    openrouter.reset()
    openrouter.slow_seconds = 0.0
    openrouter.close_connections = False
    for key, value in {
        "openrouter_api_url": openrouter.url,
        "openrouter_api_key": "test-key",
        "openrouter_model": MODEL,
        "max_retries": 2,
        "max_concurrent_requests": 3,
        "timeout": 1.0,
    }.items():
        api.portal.set_registry_record(f"interaktiv.aiclient.{key}", value)
    fresh_ai_client.reload()
    openrouter.reset()
    return fresh_ai_client
