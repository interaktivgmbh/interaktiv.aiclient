from interaktiv.aiclient.interfaces import IAIClient
from plone.base.interfaces import INonInstallable
from Products.GenericSetup.interfaces import ISetupContext
from typing import List
from zope.component import queryUtility
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self) -> List[str]:
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "interaktiv.aiclient:uninstall",
        ]

    def getNonInstallableProducts(self) -> List[str]:
        """Hide the upgrades package from site-creation and quickinstaller."""
        return [
            "interaktiv.aiclient.upgrades",
        ]


# noinspection PyUnusedLocal
def uninstall(context: ISetupContext) -> None:
    client = queryUtility(IAIClient)
    if client is not None:
        client.reset()
