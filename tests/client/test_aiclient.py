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

import asyncio
import pytest


class TestAIClient:
    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_initialisation(self, mock_chatopenai, portal):
        ai_client: AIClient = getUtility(IAIClient)

        # should fail because no API key is set
        with pytest.raises(AIClientInitializationError):
            ai_client.reload()

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )

        # should fail because no model is selected
        with pytest.raises(AIClientInitializationError):
            ai_client.reload()

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # this should not raise - both API key and model are set
        ai_client.reload()
        assert ai_client._client is not None

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_call(self, mock_chatopenai, portal):
        # setup
        mock_client_instance = mock_chatopenai.return_value

        mock_response = mock.MagicMock()
        mock_response.content = "Hello world!"

        async def mock_ainvoke(messages):
            return mock_response

        mock_client_instance.ainvoke = mock_ainvoke

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
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_client_handles_errors(self, mock_chatopenai, portal):
        # setup
        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # create new client instance with the new mocked ChatOpenAI client
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
            mock_client_instance = mock_chatopenai.return_value

            async def mock_ainvoke_error(messages, err=error_cls(**params)):
                raise err

            mock_client_instance.ainvoke = mock_ainvoke_error

            # this should not raise
            res = ai_client.call([{"role": "user", "content": "Hello!"}])

            # post condition
            assert res is None

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_batch_success(self, mock_chatopenai, portal):
        # setup
        mock_client_instance = mock_chatopenai.return_value

        async def mock_ainvoke(messages):
            response = mock.MagicMock()
            response.content = f"Response to: {messages[0]['content']}"
            return response

        mock_client_instance.ainvoke = mock_ainvoke

        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # do it
        messages_list = [
            [{"role": "user", "content": "Hello!"}],
            [{"role": "user", "content": "World!"}],
        ]
        results = ai_client.batch(messages_list)

        # post condition
        assert len(results) == 2
        assert results[0] == "Response to: Hello!"
        assert results[1] == "Response to: World!"

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_batch_partial_failure(self, mock_chatopenai, portal):
        # setup
        mock_client_instance = mock_chatopenai.return_value

        call_count = 0

        async def mock_ainvoke(messages):
            nonlocal call_count
            call_count += 1
            if "fail" in messages[0]["content"]:
                raise BadRequestError(
                    message="Test error", response=mock.MagicMock(), body=None
                )
            response = mock.MagicMock()
            response.content = f"Response to: {messages[0]['content']}"
            return response

        mock_client_instance.ainvoke = mock_ainvoke

        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )
        api.portal.set_registry_record("interaktiv.aiclient.max_retries", 2)

        # do it
        messages_list = [
            [{"role": "user", "content": "Hello!"}],
            [{"role": "user", "content": "fail"}],
            [{"role": "user", "content": "World!"}],
        ]
        results = ai_client.batch(messages_list)

        # post condition
        assert len(results) == 3
        assert results[0] == "Response to: Hello!"
        assert results[1] is None  # failed after retries
        assert results[2] == "Response to: World!"
        # 2 successful + 2 retries for the failing one
        assert call_count == 4

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_batch_timeout(self, mock_chatopenai, portal):
        # setup
        mock_client_instance = mock_chatopenai.return_value

        async def mock_ainvoke_slow(messages):
            await asyncio.sleep(10)  # longer than timeout
            response = mock.MagicMock()
            response.content = "Should not reach"
            return response

        mock_client_instance.ainvoke = mock_ainvoke_slow

        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )
        api.portal.set_registry_record("interaktiv.aiclient.max_retries", 1)
        api.portal.set_registry_record("interaktiv.aiclient.timeout", 0.1)

        # do it - short timeout
        messages_list = [[{"role": "user", "content": "Hello!"}]]
        results = ai_client.batch(messages_list)

        # post condition
        assert len(results) == 1
        assert results[0] is None  # timed out

    # noinspection PyUnusedLocal
    @mock.patch("interaktiv.aiclient.client.ChatOpenAI")
    def test_batch_retry_succeeds(self, mock_chatopenai, portal):
        # setup
        mock_client_instance = mock_chatopenai.return_value

        attempt_count = 0

        async def mock_ainvoke_flaky(messages):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise APIConnectionError(
                    message="Connection failed", request=mock.MagicMock()
                )
            response = mock.MagicMock()
            response.content = "Success after retries"
            return response

        mock_client_instance.ainvoke = mock_ainvoke_flaky

        ai_client: AIClient = getUtility(IAIClient)

        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )
        api.portal.set_registry_record("interaktiv.aiclient.max_retries", 3)

        # do it - allow 3 retries
        messages_list = [[{"role": "user", "content": "Hello!"}]]
        results = ai_client.batch(messages_list)

        # post condition
        assert len(results) == 1
        assert results[0] == "Success after retries"
        assert attempt_count == 3
