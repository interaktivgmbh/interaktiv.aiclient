from interaktiv.aiclient import _
from interaktiv.aiclient import logger
from interaktiv.aiclient.interfaces import IAIClient
from openai import APIConnectionError
from openai import APIStatusError
from openai import APITimeoutError
from openai import BadRequestError
from openai import InternalServerError
from openai import OpenAI
from openai import RateLimitError
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
        self._client: Optional[OpenAI] = None
        self._selected_model: Optional[str] = None
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
            error_message = _("No model selected.")
            raise AIClientInitializationError(f"{self.__on_failure} {error_message}")

    def reload(self) -> None:
        """
        This will re-initialise the AI Client.
        This should be called whenever the client configuration changes.
        """
        self.__ensure_initialised(force=True)

    def call(self, messages: List[Dict[str, str]]) -> Optional[str]:
        self.__ensure_initialised()
        self.__ensure_model_selected()

        try:
            completion = self._client.chat.completions.create(
                model=self._selected_model,
                messages=cast(list[ChatCompletionMessageParam], messages),
            )
            return completion.choices[0].message.content
        except BadRequestError as e:
            logger.error(f"Invalid request: {e}")
            return None
        except InternalServerError as e:
            logger.error(f"OpenAI internal server error: {e}")
            return None
        except RateLimitError as e:
            logger.error(f"Rate limit reached: {e}")
            return None
        except APITimeoutError as e:
            logger.error(f"Request timed out: {e}")
            return None
        except APIConnectionError as e:
            logger.error(f"Connection problem: {e}")
            return None
        except APIStatusError as e:
            logger.error(f"API status error {e.status_code}: {e}")
            return None

    @property
    def selected_model(self):
        return self._selected_model
