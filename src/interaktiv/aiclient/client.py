from interaktiv.aiclient import _
from interaktiv.aiclient import logger
from interaktiv.aiclient.helper import safe_execute_async
from interaktiv.aiclient.interfaces import IAIClient
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

    def __ensure_initialised(self, force: bool = False) -> None:
        if self._client and not force:
            return  # already initialised

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

        extra_body = self.__get_extra_body(self._selected_model)

        self._client = ChatOpenAI(
            base_url=api_url,
            api_key=SecretStr(api_key),
            model=self._selected_model,
            extra_body=extra_body,
        )

    def __get_registry_value(self, key: str, missing_msg: str) -> str:
        registry: Registry = getUtility(IRegistry)
        value: str = registry.get(key)

        if not value:
            raise AIClientInitializationError(
                f"{_('Failed to initialise AI Client.')} {missing_msg}"
            )

        return value

    def reload(self) -> None:
        """
        This will re-initialise the AI Client.
        This should be called whenever the client configuration changes.
        """
        self.__ensure_initialised(force=True)

    def call(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        self.__ensure_initialised()

        registry: Registry = getUtility(IRegistry)

        max_retries = registry["interaktiv.aiclient.max_retries"]
        timeout = registry["interaktiv.aiclient.timeout"]

        func = self._call_with_retry(messages, max_retries, timeout)
        return safe_execute_async(func)

    def batch(
        self,
        messages_list: List[List[Dict[str, Any]]],
    ) -> List[Optional[str]]:
        self.__ensure_initialised()

        func = self._process_batch(messages_list)
        return safe_execute_async(func)

    async def _call_with_retry(
        self,
        messages: List[Dict[str, Any]],
        max_retries: int,
        timeout: float,
    ) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self._client.ainvoke(messages),
                    timeout=timeout,
                )
                return response.content
            except asyncio.TimeoutError:
                logger.error(f"Timeout on attempt {attempt + 1}/{max_retries}")
            except (
                BadRequestError,
                InternalServerError,
                RateLimitError,
                APITimeoutError,
                APIConnectionError,
                APIStatusError,
            ) as e:
                logger.error(f"Error on attempt {attempt + 1}/{max_retries}: {e}")
        return None

    async def _process_batch(
        self,
        messages_list: List[List[Dict[str, Any]]],
    ) -> List[Optional[str]]:
        registry: Registry = getUtility(IRegistry)

        max_retries = registry["interaktiv.aiclient.max_retries"]
        timeout = registry["interaktiv.aiclient.timeout"]

        tasks = [
            self._call_with_retry(messages, max_retries, timeout)
            for messages in messages_list
        ]

        result = await asyncio.gather(*tasks)
        return list(result)

    @staticmethod
    def __get_extra_body(model: str) -> Optional[Dict[str, Any]]:
        if model.startswith("mistralai/"):
            return {"provider": {"only": ["Mistral"]}}
        return None

    @property
    def selected_model(self):
        return self._selected_model
