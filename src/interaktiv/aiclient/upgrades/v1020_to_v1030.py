from Products.GenericSetup.tool import SetupTool
from typing import Optional

import plone.api as api


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> None:
    record = "interaktiv.aiclient.max_concurrent_requests"

    # raise existing default value for maximum concurrent requests from 5 to 10
    if api.portal.get_registry_record(record, default=None) == 5:
        api.portal.set_registry_record(record, 10)
