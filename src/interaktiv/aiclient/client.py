from interaktiv.aiclient.interfaces import IAIClient
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from zope.interface import implementer
from zope.component import getUtility


@implementer(IAIClient)
class AIClient:
    def call(self):
        registry: Registry = getUtility(IRegistry)
        selected_model = registry.get("interaktiv.aiclient.openrouter_model")

        print(selected_model)
