"""Module where all interfaces, events and exceptions live."""

from typing import Dict
from typing import List
from typing import Optional
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IInteraktivAIClientBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAIClient(Interface):
    """AI Client Singleton"""

    def call(self, messages: List[Dict[str, str]]) -> Optional[str]: ...
