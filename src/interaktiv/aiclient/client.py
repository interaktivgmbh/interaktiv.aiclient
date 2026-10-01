from concurrent.futures import ThreadPoolExecutor
from interaktiv.aiclient import _
from interaktiv.aiclient import logger
from interaktiv.aiclient.interfaces import IAIClient
from interaktiv.aiclient.types import BatchPrompts
from interaktiv.aiclient.types import BatchResponse
from interaktiv.aiclient.types import Prompt
from interaktiv.aiclient.types import Response
from openai import APIError
from openai import OpenAI
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from typing import Any
from typing import Dict
from typing import Optional
from zope.component import getUtility
from zope.interface import implementer

import inspect
import threading


# request parameters the client sets itself
RESERVED_OPTIONS = frozenset({"model", "messages", "stream"})


class AIClientInitializationError(Exception):
    pass


@implementer(IAIClient)
class AIClient:
    def __init__(self) -> None:
        self._client: Optional[OpenAI] = None
        self._selected_model: Optional[str] = None
        self._extra_body: Optional[Dict[str, Any]] = None
        self._max_retries: Optional[int] = None
        self._max_concurrent_requests: Optional[int] = None
        self._timeout: Optional[float] = None
        self._lock = threading.Lock()

    def __ensure_initialised(self, force: bool = False) -> None:
        if self._client and not force:
            return  # already initialised

        with self._lock:
            # checked again because another thread may have initialised
            # the client while this one waited for the lock
            if self._client and not force:
                return

            registry: Registry = getUtility(IRegistry)

            api_url = self.__get_registry_value(
                key="interaktiv.aiclient.openrouter_api_url",
                missing_msg=_("No API URL provided."),
            )
            api_key = self.__get_registry_value(
                key="interaktiv.aiclient.openrouter_api_key",
                missing_msg=_("No API Key provided."),
            )
            selected_model = self.__get_registry_value(
                key="interaktiv.aiclient.openrouter_model",
                missing_msg=_("No model selected."),
            )

            self._max_retries = registry.get("interaktiv.aiclient.max_retries", 3)
            self._max_concurrent_requests = registry.get(
                "interaktiv.aiclient.max_concurrent_requests", 10
            )
            self._timeout = registry.get("interaktiv.aiclient.timeout", 60.0)
            self._extra_body = self.__get_extra_body(selected_model)
            self._selected_model = selected_model

            self._client = OpenAI(
                base_url=api_url,
                api_key=api_key,
                max_retries=self._max_retries,
                timeout=self._timeout,
            )

    def reload(self) -> None:
        """
        This will re-initialise the AI Client.
        This should be called whenever the client configuration changes.
        """
        self.__ensure_initialised(force=True)

    def call(self, messages: Prompt, **options: Any) -> Response:
        """Send one prompt.

        `options` are passed to the chat completions request, e.g.
        `max_tokens=500`; OpenRouter-only parameters go into `extra_body`.
        """
        self.__ensure_initialised()
        self._check_options(options)
        return self._call_with_retry(messages, **options)

    def batch(self, prompts: BatchPrompts, **options: Any) -> BatchResponse:
        """Send several prompts concurrently, with the same `options` each."""
        self.__ensure_initialised()
        self._check_options(options)

        if not prompts:
            return []

        workers = max(1, min(self._max_concurrent_requests or 1, len(prompts)))
        with ThreadPoolExecutor(
            max_workers=workers, thread_name_prefix="aiclient"
        ) as executor:
            futures = [
                executor.submit(self._call_with_retry, prompt, **options)
                for prompt in prompts
            ]
        return [
            future.exception() if future.exception() else future.result()
            for future in futures
        ]

    def _check_options(self, options: Dict[str, Any]) -> None:
        reserved = RESERVED_OPTIONS.intersection(options)

        if reserved:
            raise TypeError(f"Options set by the AI client: {sorted(reserved)}")

        signature = inspect.signature(self._client.chat.completions.create)
        signature.bind_partial(**options)

    def _call_with_retry(self, messages: Optional[Prompt], **options: Any) -> Response:
        """Send one prompt. Retries happen inside the OpenAI client."""
        if not messages:
            return None

        # the caller's extra_body wins over the provider routing
        extra_body = {**(self._extra_body or {}), **options.pop("extra_body", {})}
        try:
            response = self._client.chat.completions.create(
                model=self._selected_model,
                messages=messages,
                stream=False,
                extra_body=extra_body,
                **options,
            )
        except APIError as e:
            logger.error(f"Request failed after {self._max_retries} retries: {e}")
            return None

        return response_content(response.model_dump())

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
        # other providers of Mistral models proved unreliable
        if model.startswith("mistralai/"):
            return {"provider": {"only": ["Mistral"]}}
        return None

    @property
    def selected_model(self):
        return self._selected_model


def response_content(response: Dict[str, Any]) -> str:
    if response.get("error"):
        raise ValueError(response["error"])
    try:
        choices = response["choices"]
    except KeyError as e:
        raise KeyError(f"Response missing `choices` key: {response.keys()}") from e
    if choices is None:
        raise TypeError("Received response with null value for `choices`.")
    return choices[0]["message"].get("content") or ""
