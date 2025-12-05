from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.client import AIClientInitializationError
from interaktiv.aiclient.interfaces import IAIClient
from openai import APIConnectionError
from openai import APIStatusError
from openai import APITimeoutError
from openai import BadRequestError
from openai import InternalServerError
from openai import RateLimitError
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
        assert ai_client.selected_model == "google/gemini-2.5-flash-image"

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.OpenAI")
    def test_client_handles_errors(self, mock_openai, portal):
        # setup
        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # create new client instance with the new mocked OpenAI client
        ai_client.reload()

        api_status_error_params = {
            "message": "Test error",
            "response": mock.MagicMock(),
            "body": None,
        }

        errors = {
            APIStatusError: api_status_error_params,
            APITimeoutError: {"request": mock.MagicMock()},
            APIConnectionError: {"message": "Test error", "request": mock.MagicMock()},
            RateLimitError: api_status_error_params,
            BadRequestError: api_status_error_params,
            InternalServerError: api_status_error_params,
        }

        # do it
        for error_cls, params in errors.items():
            mock_client_instance = mock_openai.return_value
            mock_client_instance.chat.completions.create.side_effect = error_cls(
                **params
            )

            # this should not raise
            res = ai_client.call([{"role": "user", "content": "Hello!"}])

            # post condition
            assert res is None
