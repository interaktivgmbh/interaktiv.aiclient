from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.controlpanels.client_settings import IAIClientSettings
from interaktiv.aiclient.interfaces import IAIClient
from plone.registry.interfaces import IRecordModifiedEvent
from typing import Optional
from zope.component import adapter
from zope.component import getUtility


# noinspection PyUnusedLocal
@adapter(IAIClientSettings, IRecordModifiedEvent)
def aiclient_settings_modified(context, event: IRecordModifiedEvent) -> None:
    ai_client: Optional[AIClient] = getUtility(IAIClient)

    ai_client.call()
