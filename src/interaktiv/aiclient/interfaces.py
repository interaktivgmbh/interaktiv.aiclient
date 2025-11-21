"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IInteraktivAIClientBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAIClient(Interface):
    """AI Client Singleton"""

    def call(self):
        raise NotImplementedError
