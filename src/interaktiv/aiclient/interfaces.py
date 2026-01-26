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

    def call(self, messages: List[Dict[str, Any]]) -> Optional[str]: ...

    def batch(
        self,
        messages_list: List[List[Dict[str, Any]]],
        max_retries: int = 3,
        timeout: float = 60.0,
    ) -> List[Optional[str]]: ...
