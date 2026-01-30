from Products.GenericSetup.tool import SetupTool
from typing import Optional

import plone.api as api


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> None:
    portal_setup = api.portal.get_tool("portal_setup")

    portal_setup.runImportStepFromProfile(
        profile_id="profile-interaktiv.aiclient:default", step_id="plone.app.registry"
    )
