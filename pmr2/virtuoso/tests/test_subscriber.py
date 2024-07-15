import unittest

import zope.component
import zope.interface
import zope.event

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.workspace.event import Push
from pmr2.app.workspace.interfaces import IStorageUtility

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso import subscriber

from pmr2.virtuoso.testing.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER


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
        self.assertEqual(
            self.engine.stmts[0],
            u'CLEAR GRAPH <urn:pmr:virtuoso:/plone/workspace/virtuoso_test>'
        )
        self.assertEqual(
            ' '.join(self.engine.stmts[1].split()),
            u'INSERT INTO <urn:pmr:virtuoso:/plone/workspace/virtuoso_test> { '
                '<simple.rdf#test> <http://purl.org/dc/elements/1.1/title> '
                    '"Test Node" .'
            ' }'
        )

    def test_workspace_rdf_indexer_event(self):
        zope.event.notify(Push(self.context))
        self.assertEqual(len(self.engine.stmts), 2)

    def test_workspace_rdf_indexer_event_file_not_exist(self):
        # emulate a previous commit that allowed this to be
        # specified by the user.
        su = zope.component.getUtility(IStorageUtility, name='dummy_storage')
        su._dummy_storage_data['virtuoso_test'][0]['does_not_exist.rdf'] = ''
        rdfinfo = zope.component.getAdapter(self.context, IWorkspaceRDFInfo)
        rdfinfo.paths = ['does_not_exist.rdf']
        su._dummy_storage_data['virtuoso_test'][0].pop('does_not_exist.rdf')

        zope.event.notify(Push(self.context))
        # data should be purged and none will be added.
        self.assertEqual(self.engine.stmts, [
            u'CLEAR GRAPH <urn:pmr:virtuoso:/plone/workspace/virtuoso_test>'
        ])
