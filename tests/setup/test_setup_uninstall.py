from interaktiv.aiclient import PACKAGE_NAME

import pytest


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product(PACKAGE_NAME)

    def test_addon_uninstalled(self, installer):
        """Test if interaktiv.aiclient is uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_browserlayer_not_registered(self, browser_layers):
        """Test that IBrowserLayer is not registered."""
        from interaktiv.aiclient.interfaces import IInteraktivAIClientBrowserLayer

        assert IInteraktivAIClientBrowserLayer not in browser_layers
