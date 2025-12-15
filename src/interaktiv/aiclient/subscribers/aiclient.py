from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.client import AIClientInitializationError
from interaktiv.aiclient.controlpanels.client_settings import IAIClientSettings
from interaktiv.aiclient.interfaces import IAIClient
from plone.registry.interfaces import IRecordModifiedEvent
from zope.component import adapter
from zope.component import getUtility

import contextlib


# noinspection PyUnusedLocal
@adapter(IAIClientSettings, IRecordModifiedEvent)
def aiclient_settings_modified(context, event: IRecordModifiedEvent) -> None:
    ai_client: AIClient = getUtility(IAIClient)

    with contextlib.suppress(AIClientInitializationError):
        ai_client.reload()
