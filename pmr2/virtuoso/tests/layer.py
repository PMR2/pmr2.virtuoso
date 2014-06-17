from os.path import dirname, join

import zope.component

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.interfaces import TEST_USER_ID
from plone.app.testing import helpers

from pmr2.app.workspace.content import WorkspaceContainer
from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.interfaces import IStorageUtility

from pmr2.app.workspace.tests.layer import WORKSPACE_BASE_FIXTURE


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

PMR2_VIRTUOSO_FIXTURE = VirtuosoLayer()

PMR2_VIRTUOSO_INTEGRATION_LAYER = IntegrationTesting(
    bases=(PMR2_VIRTUOSO_FIXTURE,), name="pmr2.virtuoso:integration",)
