from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.client import AIClientInitializationError
from plone import api

import pytest


def user(text):
    return [{"role": "user", "content": text}]


class TestAIClient:
    # noinspection PyUnusedLocal
    def test_initialisation(self, portal, fresh_ai_client):
        # pre condition
        # should fail because no API key is set
        with pytest.raises(AIClientInitializationError):
            fresh_ai_client.reload()

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )

        # should fail because no model is selected
        with pytest.raises(AIClientInitializationError):
            fresh_ai_client.reload()

        # setup
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # do it
        fresh_ai_client.reload()

        # post condition
        assert fresh_ai_client._client is not None
        assert fresh_ai_client.selected_model == "google/gemini-2.5-flash-image"

    # noinspection PyUnusedLocal
    def test_call_without_configuration(self, portal, fresh_ai_client):
        # do it
        with pytest.raises(AIClientInitializationError):
            fresh_ai_client.call(user("Hello"))

    # noinspection PyUnusedLocal
    def test_batch_without_configuration(self, portal, fresh_ai_client):
        # do it
        with pytest.raises(AIClientInitializationError):
            fresh_ai_client.batch([user("Hello")])

    def test_reload_applies_new_settings(self, ai_client, openrouter):
        # setup
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "mistralai/mistral-small"
        )

        # do it
        ai_client.reload()
        ai_client.call(user("Hello"))

        # post condition
        body = openrouter.bodies[-1]
        assert body["model"] == "mistralai/mistral-small"
        assert body["provider"] == {"only": ["Mistral"]}

    # noinspection PyUnusedLocal
    def test_call(self, ai_client: AIClient, openrouter):
        # do it
        res = ai_client.call(user("Hello!"))

        # post condition
        assert res == "echo: Hello!"
        assert ai_client.selected_model == "google/gemini-2.5-flash-image"

    def test_call_sends_key_and_model(self, ai_client, openrouter):
        # do it
        ai_client.call(user("Hello!"))

        # post condition
        _, headers, body = openrouter.requests[-1]
        assert headers["authorization"] == "Bearer test-key"
        assert body == {
            "model": "google/gemini-2.5-flash-image",
            "messages": [{"role": "user", "content": "Hello!"}],
            "stream": False,
        }

    @pytest.mark.parametrize("marker", ["case:400", "case:429", "case:500"])
    def test_client_handles_errors(self, ai_client, marker):
        # do it
        res = ai_client.call(user(marker))

        # post condition
        assert res is None

    def test_client_handles_timeout(self, ai_client, openrouter):
        # setup
        openrouter.slow_seconds = 1.5

        # do it
        res = ai_client.call(user("case:slow"))

        # post condition
        assert res is None

    def test_client_handles_unreachable_server(self, ai_client):
        # setup
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_url", "http://127.0.0.1:9/api/v1"
        )
        ai_client.reload()

        # do it
        res = ai_client.call(user("Hello"))

        # post condition
        assert res is None

    def test_batch_success(self, ai_client):
        # setup
        prompts = [user(f"case:sleep {i}") for i in range(6)]

        # do it
        results = ai_client.batch(prompts)

        # post condition
        assert results == [f"echo: case:sleep {i}" for i in range(6)]

    def test_batch_partial_failure(self, ai_client):
        # setup
        prompts = [
            user("Hello!"),
            user("case:400"),
            None,
            [],
            user("case:err200"),
            user("World!"),
        ]

        # do it
        results = ai_client.batch(prompts)

        # post condition
        assert len(results) == 6
        assert results[0] == "echo: Hello!"
        assert results[1] is None  # API error
        assert results[2] is None  # no prompt
        assert results[3] is None  # empty prompt
        assert isinstance(results[4], ValueError)  # error payload, as exception
        assert results[5] == "echo: World!"

    def test_batch_empty(self, ai_client, openrouter):
        # do it
        results = ai_client.batch([])

        # post condition
        assert results == []
        assert openrouter.requests == []
