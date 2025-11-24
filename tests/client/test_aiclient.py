from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.client import AIClientInitializationError
from interaktiv.aiclient.interfaces import IAIClient
from plone import api
from unittest import mock
from zope.component import getUtility

import pytest


class TestAIClient:
    # noinspection PyUnusedLocal
    def test_initialisation(self, portal):
        ai_client: AIClient = getUtility(IAIClient)

        with pytest.raises(AIClientInitializationError):
            ai_client.reload()

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )

        # this should not raise
        ai_client.reload()
        assert ai_client._client is not None

        # this should fail because no model is selected
        with pytest.raises(AIClientInitializationError):
            ai_client.call([...])

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.OpenAI")
    def test_call(self, mock_openai, portal):
        # setup
        mock_client_instance = mock_openai.return_value

        mock_completion = mock.MagicMock()
        mock_completion.choices = [
            mock.MagicMock(message=mock.MagicMock(content="Hello world!"))
        ]

        mock_client_instance.chat.completions.create.return_value = mock_completion

        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # do it
        res = ai_client.call([{"role": "user", "content": "Hello!"}])

        # post condition
        assert res == "Hello world!"
