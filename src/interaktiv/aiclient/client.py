from interaktiv.aiclient import _
from interaktiv.aiclient import logger
from interaktiv.aiclient.helper import safe_execute_async
from interaktiv.aiclient.interfaces import IAIClient
from interaktiv.aiclient.types import BatchPrompts
from interaktiv.aiclient.types import BatchResponse
from interaktiv.aiclient.types import Prompt
from interaktiv.aiclient.types import Response
from langchain_openai import ChatOpenAI
from openai import APIConnectionError
from openai import APIStatusError
from openai import APITimeoutError
from openai import BadRequestError
from openai import InternalServerError
from openai import RateLimitError
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from pydantic import SecretStr
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from zope.component import getUtility
from zope.interface import implementer

import asyncio


class AIClientInitializationError(Exception):
    pass


@implementer(IAIClient)
class AIClient:
    def __init__(self) -> None:
        self._client: Optional[ChatOpenAI] = None
        self._selected_model: Optional[str] = None
        self._max_retries: Optional[int] = None
        self._timeout: float = 60.0

    def __ensure_initialised(self, force: bool = False) -> None:
        if self._client and not force:
            return  # already initialised

        registry: Registry = getUtility(IRegistry)

        api_url = self.__get_registry_value(
            key="interaktiv.aiclient.openrouter_api_url",
            missing_msg=_("No API URL provided."),
        )
        api_key = self.__get_registry_value(
            key="interaktiv.aiclient.openrouter_api_key",
            missing_msg=_("No API Key provided."),
        )
        self._selected_model = self.__get_registry_value(
            key="interaktiv.aiclient.openrouter_model",
            missing_msg=_("No model selected."),
        )

        self._max_retries = registry.get("interaktiv.aiclient.max_retries", 3)
        self._timeout = registry.get("interaktiv.aiclient.timeout", 60.0)

        extra_body = self.__get_extra_body(self._selected_model)

        self._client = ChatOpenAI(
            base_url=api_url,
            api_key=SecretStr(api_key),
            model=self._selected_model,
            extra_body=extra_body,
        )

    def reload(self) -> None:
        """
        This will re-initialise the AI Client.
        This should be called whenever the client configuration changes.
        """
        self.__ensure_initialised(force=True)

    def call(self, messages: Prompt) -> Response:
        self.__ensure_initialised()

        func = self._call_with_retry(messages)
        return safe_execute_async(func)

    def batch(self, prompts: BatchPrompts) -> BatchResponse:
        self.__ensure_initialised()

        func = self._process_batch(prompts)
        return safe_execute_async(func)

    async def _call_with_retry(self, messages: Prompt) -> Response:
        if not messages:
            return None

        for attempt in range(self._max_retries):
            try:
                response = await asyncio.wait_for(
                    self._client.ainvoke(messages),
                    timeout=self._timeout,
                )
                return response.content
            except asyncio.TimeoutError:
                logger.error(f"Timeout on attempt {attempt + 1}/{self._max_retries}")
            except (
                BadRequestError,
                InternalServerError,
                RateLimitError,
                APITimeoutError,
                APIConnectionError,
                APIStatusError,
            ) as e:
                logger.error(f"Error on attempt {attempt + 1}/{self._max_retries}: {e}")
        return None

    async def _process_batch(self, prompts: BatchPrompts) -> BatchResponse:
        tasks = [self._call_with_retry(prompt) for prompt in prompts]

        result = await asyncio.gather(*tasks, return_exceptions=True)

        return list(result)

    @staticmethod
    def __get_registry_value(key: str, missing_msg: str) -> Any:
        registry: Registry = getUtility(IRegistry)

        try:
            value: Any = registry[key]
        except KeyError:
            value = None

        if value is None:
            raise AIClientInitializationError(
                f"{_('Failed to initialise AI Client.')} {missing_msg}"
            )

        return value

    @staticmethod
    def __get_extra_body(model: str) -> Optional[Dict[str, Any]]:
        if model.startswith("mistralai/"):
            return {"provider": {"only": ["Mistral"]}}
        return None

    @property
    def selected_model(self):
        return self._selected_model
