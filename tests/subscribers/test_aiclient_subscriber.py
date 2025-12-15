from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.interfaces import IAIClient
from plone import api
from zope.component import getUtility


class TestAIClientSubscriber:
    # noinspection PyUnusedLocal
    def test_ai_client_reloaded(self, portal):
        # setup
        ai_client: AIClient = getUtility(IAIClient)

        # pre condition
        assert ai_client._client is None
        assert ai_client._selected_model is None

        # do it
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_api_key", "api_key"
        )
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "google/gemini-2.5-flash-image"
        )

        # post condition
        assert ai_client._client is not None
        assert ai_client._selected_model == "google/gemini-2.5-flash-image"
