from os.path import dirname, join

import zope.component

from Testing import ZopeTestCase as ztc
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup, onteardown
from Products.PloneTestCase import PloneTestCase as ptc

from pmr2.app.workspace.content import WorkspaceContainer, Workspace
from pmr2.app.workspace.interfaces import IStorageUtility

import pmr2.testing
from pmr2.app.workspace.tests.base import WorkspaceDocTestCase


@onsetup
def setup():
    import pmr2.virtuoso
    fiveconfigure.debug_mode = True
    zcml.load_config('test.zcml', pmr2.testing)
    zcml.load_config('configure.zcml', pmr2.virtuoso)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.virtuoso')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.virtuoso'))


class WorkspaceRDFTestCase(WorkspaceDocTestCase):

    def setUp(self):
        super(WorkspaceRDFTestCase, self).setUp()
        su = zope.component.getUtility(IStorageUtility, name='dummy_storage')
        su._loadDir('virtuoso_test', join(dirname(__file__), 'data'))

        from pmr2.virtuoso.tests.engine import Engine
        zope.component.provideAdapter(Engine())
        self.portal['workspace'] = WorkspaceContainer()
        w = Workspace('virtuoso_test')
        w.storage = 'dummy_storage' 
        self.portal.workspace['virtuoso_test'] = w
