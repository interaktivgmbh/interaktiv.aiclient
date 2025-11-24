from interaktiv.aiclient import _
from interaktiv.aiclient.interfaces import IAIClient
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from zope.component import getUtility
from zope.interface import implementer


class AIClientInitializationError(Exception):
    pass


@implementer(IAIClient)
class AIClient:
    def __init__(self) -> None:
        self._client = None
        self._selected_model = None
        self.__on_failure = _("Failed to initialise AI Client.")

    def __ensure_initialised(self, force: bool = False) -> None:
        if self._client and not force:
            return  # already initialised

        registry: Registry = getUtility(IRegistry)

        api_url = self.__get_registry_value(
            registry=registry,
            key="interaktiv.aiclient.openrouter_api_url",
            missing_msg=_("No API URL provided."),
        )

        api_key = self.__get_registry_value(
            registry=registry,
            key="interaktiv.aiclient.openrouter_api_key",
            missing_msg=_("No API Key provided."),
        )

        self._selected_model = registry.get("interaktiv.aiclient.openrouter_model")
        self._client = OpenAI(base_url=api_url, api_key=api_key)

    def __get_registry_value(
        self, registry: Registry, key: str, missing_msg: str
    ) -> str:
        value: str = registry.get(key)

        if not value:
            raise AIClientInitializationError(f"{self.__on_failure} {missing_msg}")

        return value

    def __ensure_model_selected(self) -> None:
        if not self._selected_model:
            raise AIClientInitializationError(f"{self.__on_failure} No model selected.")

    def reload(self) -> None:
        """
        This will re-initialise the AI Client.
        This should be called whenever the client configuration changes.
        """
        self.__ensure_initialised(force=True)

    def call(self, messages: List[Dict[str, str]]) -> Optional[str]:
        self.__ensure_initialised()
        self.__ensure_model_selected()

        completion = self._client.chat.completions.create(
            model=self._selected_model,
            messages=cast(list[ChatCompletionMessageParam], messages),
        )

        return completion.choices[0].message.content
