import unittest

import zope.component
import zope.interface
import zope.event

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.workspace.event import Push

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso import subscriber

from pmr2.virtuoso.tests.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER


class WorkspaceSubscriberTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def setUp(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        self.engine = zope.component.getAdapter(settings, IEngine)
        self.engine._clear()

        self.context = self.layer['portal'].workspace['virtuoso_test']
        rdfinfo = zope.component.getAdapter(self.context, IWorkspaceRDFInfo)
        rdfinfo.paths = ['simple.rdf']

    def test_workspace_rdf_indexer(self):
        event = None
        subscriber.reindex_workspace_rdf(self.context, event)

        self.assertEqual(len(self.engine.stmts), 2)
        self.assertEqual(self.engine.stmts[0], 'SPARQL '
            u'CLEAR GRAPH <urn:pmr:virtuoso:/plone/workspace/virtuoso_test>')
        self.assertEqual(' '.join(self.engine.stmts[1].split()), u'SPARQL '
            u'INSERT INTO <urn:pmr:virtuoso:/plone/workspace/virtuoso_test> { '
                '<#test> <http://purl.org/dc/elements/1.1/title> "Test Node" .'
            ' }')

    def test_workspace_rdf_indexer_event(self):
        zope.event.notify(Push(self.context))
        self.assertEqual(len(self.engine.stmts), 2)
