from interaktiv.aiclient import PACKAGE_NAME
from interaktiv.aiclient.client import AIClientInitializationError
from plone import api

import pytest


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer, ai_client, openrouter):
        ai_client.call([{"role": "user", "content": "Hello"}])
        installer.uninstall_product(PACKAGE_NAME)
        openrouter.reset()

    def test_addon_uninstalled(self, installer):
        """Test if interaktiv.aiclient is uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_browserlayer_not_registered(self, browser_layers):
        """Test that IBrowserLayer is not registered."""
        from interaktiv.aiclient.interfaces import IInteraktivAIClientBrowserLayer

        assert IInteraktivAIClientBrowserLayer not in browser_layers

    def test_settings_removed(self):
        # do it
        api_key = api.portal.get_registry_record(
            "interaktiv.aiclient.openrouter_api_key", default=None
        )

        # post condition
        assert api_key is None

    def test_controlpanel_removed(self):
        # do it
        configlets = api.portal.get_tool("portal_controlpanel").listActions()

        # post condition
        assert "aiclient-controlpanel" not in [c.getId() for c in configlets]

    def test_client_forgets_the_api_key(self, ai_client, openrouter):
        # do it
        with pytest.raises(AIClientInitializationError):
            ai_client.call([{"role": "user", "content": "Hello"}])

        # post condition
        assert openrouter.requests == []
