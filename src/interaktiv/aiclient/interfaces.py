"""Module where all interfaces, events and exceptions live."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IInteraktivAIClientBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAIClient(Interface):
    """AI Client Singleton"""

    selected_model: Optional[str]
    """The currently selected model identifier, or None if not initialized."""

    def reload() -> None:
        """Re-initialize the client with current configuration."""

    def reset() -> None:
        """Forget the client and its configuration until the next use."""

    def call(messages: List[Dict[str, Any]], **options) -> Optional[str]:
        """Sends a prompt to the AI model and return the response.

        Keyword options are passed to the chat completions request.
        """

    def batch(
        messages_list: List[List[Dict[str, Any]]], **options
    ) -> List[Optional[str]]:
        """Send multiple prompts concurrently and return all responses."""
