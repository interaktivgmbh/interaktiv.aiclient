from interaktiv.aiclient.upgrades import v1000_to_v1010
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestUpgrades:
    # noinspection PyUnusedLocal
    def test_upgrade_v1000_to_v1010(self, portal):
        # setup
        registry = getUtility(IRegistry)
        del registry.records["interaktiv.aiclient.max_retries"]
        del registry.records["interaktiv.aiclient.timeout"]

        # pre condition
        max_retries = api.portal.get_registry_record(
            name="interaktiv.aiclient.max_retries", default=None
        )
        timeout = api.portal.get_registry_record(
            name="interaktiv.aiclient.timeout", default=None
        )
        assert max_retries is None
        assert timeout is None

        # do it
        v1000_to_v1010.upgrade(None)

        # post condition
        max_retries = api.portal.get_registry_record(
            name="interaktiv.aiclient.max_retries"
        )
        timeout = api.portal.get_registry_record(name="interaktiv.aiclient.timeout")
        assert max_retries == 3
        assert timeout == 60.0
