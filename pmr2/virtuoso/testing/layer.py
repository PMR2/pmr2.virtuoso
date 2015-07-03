from os.path import dirname, join

import zope.component

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.interfaces import TEST_USER_ID
from plone.app.testing import helpers

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from pmr2.app.workspace.content import WorkspaceContainer
from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.workspace.tests.layer import WORKSPACE_BASE_FIXTURE
from pmr2.app.exposure.tests.layer import EXPOSURE_FIXTURE

from pmr2.virtuoso.browser.client import SparqlClientForm
from pmr2.virtuoso.interfaces import ISparqlClient
from pmr2.virtuoso.interfaces import ISettings

from pmr2.virtuoso.testing.dummy import DummyPortalSparqlClient


class VirtuosoLayer(PloneSandboxLayer):

    defaultBases = (WORKSPACE_BASE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import pmr2.virtuoso
        self.loadZCML(package=pmr2.virtuoso)

        # until pmr2.z3cform has a layer, this is needed to fully render
        # the forms.
        import pmr2.z3cform.tests
        self.loadZCML('testing.zcml', package=pmr2.z3cform.tests)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'pmr2.virtuoso:default')

        su = zope.component.getUtility(IStorageUtility, name='dummy_storage')
        su._loadDir('virtuoso_test', join(dirname(__file__), 'data'))

        from pmr2.virtuoso.tests.engine import Engine
        zope.component.provideAdapter(Engine())

        w = Workspace('virtuoso_test')
        w.storage = 'dummy_storage' 
        portal.workspace['virtuoso_test'] = w

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        self.settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        self.default_client = zope.component.getMultiAdapter(
            (portal, self.settings), ISparqlClient)
        sm = portal.getSiteManager()
        sm.unregisterAdapter(self.default_client, (IPloneSiteRoot, ISettings),
            ISparqlClient)
        sm.registerAdapter(DummyPortalSparqlClient,
            (IPloneSiteRoot, ISettings), ISparqlClient)

    def tearDownPloneSite(self, portal):
        sm = portal.getSiteManager()
        sm.unregisterAdapter(DummyPortalSparqlClient,
            (IPloneSiteRoot, ISettings), ISparqlClient)
        sm.registerAdapter(self.default_client, (IPloneSiteRoot, ISettings),
            ISparqlClient)

PMR2_VIRTUOSO_FIXTURE = VirtuosoLayer()

PMR2_VIRTUOSO_INTEGRATION_LAYER = IntegrationTesting(
    bases=(PMR2_VIRTUOSO_FIXTURE,), name="pmr2.virtuoso:integration",)


class VirtuosoExposureLayer(PloneSandboxLayer):

    defaultBases = (PMR2_VIRTUOSO_FIXTURE,) # EXPOSURE_FIXTURE,)

    def setUpPloneSite(self, portal):
        from pmr2.app.exposure.content import Exposure
        from pmr2.app.exposure.content import ExposureContainer
        from pmr2.app.exposure.content import ExposureFile

        # Using a separate container because of inability for layers to
        # actually isolate from each other during tearing down when
        # multiple defaultBases (or bases) are used, (especially when
        # running as part of the entire test) and that they
        # somehow persist through tearDown.

        portal['virtuoso_exposure'] = ExposureContainer('virtuoso_exposure')

        e = Exposure('virtuoso_test')
        e.workspace = u'/plone/workspace/virtuoso_test'
        e.commit_id = u'0'
        portal.virtuoso_exposure['virtuoso_test'] = e
        portal.virtuoso_exposure['virtuoso_test'].reindexObject()

        ef = ExposureFile('simple.rdf')
        portal.virtuoso_exposure.virtuoso_test['simple.rdf'] = ef

PMR2_VIRTUOSO_EXPOSURE_FIXTURE = VirtuosoExposureLayer()

PMR2_VIRTUOSO_EXPOSURE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(PMR2_VIRTUOSO_EXPOSURE_FIXTURE,),
    name="pmr2.virtuoso:integration_exposure",
)
