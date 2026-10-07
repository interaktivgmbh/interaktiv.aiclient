from interaktiv.aiclient.upgrades import update_registry
from interaktiv.aiclient.upgrades import v1020_to_v1030
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


MAX_CONCURRENT_REQUESTS = "interaktiv.aiclient.max_concurrent_requests"


class TestUpgrades:
    # noinspection PyUnusedLocal
    def test_upgrade_update_registry(self, portal):
        # setup
        registry = getUtility(IRegistry)
        del registry.records["interaktiv.aiclient.max_retries"]
        del registry.records["interaktiv.aiclient.max_concurrent_requests"]
        del registry.records["interaktiv.aiclient.timeout"]

        # pre condition
        max_retries = api.portal.get_registry_record(
            name="interaktiv.aiclient.max_retries", default=None
        )
        max_concurrent_requests = api.portal.get_registry_record(
            name="interaktiv.aiclient.max_concurrent_requests", default=None
        )
        timeout = api.portal.get_registry_record(
            name="interaktiv.aiclient.timeout", default=None
        )
        assert max_retries is None
        assert max_concurrent_requests is None
        assert timeout is None

        # do it
        update_registry.upgrade(None)

        # post condition
        max_retries = api.portal.get_registry_record(
            name="interaktiv.aiclient.max_retries"
        )
        max_concurrent_requests = api.portal.get_registry_record(
            name="interaktiv.aiclient.max_concurrent_requests"
        )
        timeout = api.portal.get_registry_record(name="interaktiv.aiclient.timeout")
        assert max_retries == 3
        assert max_concurrent_requests == 10
        assert timeout == 60.0

    # noinspection PyUnusedLocal
    def test_upgrade_v1030_raises_old_default(self, portal):
        # setup
        api.portal.set_registry_record(MAX_CONCURRENT_REQUESTS, 5)

        # do it
        v1020_to_v1030.upgrade(None)

        # post condition
        assert api.portal.get_registry_record(MAX_CONCURRENT_REQUESTS) == 10

    # noinspection PyUnusedLocal
    def test_upgrade_v1030_keeps_non_default_value(self, portal):
        # setup
        api.portal.set_registry_record(MAX_CONCURRENT_REQUESTS, 3)

        # do it
        v1020_to_v1030.upgrade(None)

        # post condition
        assert api.portal.get_registry_record(MAX_CONCURRENT_REQUESTS) == 3
