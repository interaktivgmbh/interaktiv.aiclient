from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE

import interaktiv.aiclient


class Layer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=interaktiv.aiclient)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "interaktiv.aiclient:default")


FIXTURE = Layer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="Interaktiv.AIClientLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="Interaktiv.AIClientLayer:FunctionalTesting",
)


ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="Interaktiv.AIClientLayer:AcceptanceTesting",
)
