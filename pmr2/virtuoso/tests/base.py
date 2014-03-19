from os.path import dirname, join

import zope.component

from Testing import ZopeTestCase as ztc
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup, onteardown
from Products.PloneTestCase import PloneTestCase as ptc

from pmr2.app.workspace.content import WorkspaceContainer, Workspace

import pmr2.testing
from pmr2.app.workspace.tests.base import WorkspaceDocTestCase
from pmr2.app.workspace.tests import storage


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

r1 = {}

for fn in ['special_cases.xml', 'simple.n3', 'simple.rdf', 'embedded.rdf']:
    with open(join(dirname(__file__), 'data', fn)) as fd:
        r1[fn] = fd.read()

storage.DummyStorageUtility._dummy_storage_data['virtuoso_test'] = [r1]


class WorkspaceRDFTestCase(WorkspaceDocTestCase):

    def setUp(self):
        super(WorkspaceRDFTestCase, self).setUp()
        from pmr2.virtuoso.tests.engine import Engine
        zope.component.provideAdapter(Engine())
        self.portal['workspace'] = WorkspaceContainer()
        w = Workspace('virtuoso_test')
        w.storage = 'dummy_storage' 
        self.portal.workspace['virtuoso_test'] = w
