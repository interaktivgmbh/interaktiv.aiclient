from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.client import AIClientInitializationError
from interaktiv.aiclient.controlpanels.client_settings import IAIClientSettings
from interaktiv.aiclient.interfaces import IAIClient
from plone.registry.interfaces import IRecordModifiedEvent
from zope.component import adapter
from zope.component import getUtility


# noinspection PyUnusedLocal
@adapter(IAIClientSettings, IRecordModifiedEvent)
def aiclient_settings_modified(context, event: IRecordModifiedEvent) -> None:
    ai_client: AIClient = getUtility(IAIClient)

    try:
        ai_client.reload()
    except AIClientInitializationError:
        pass
