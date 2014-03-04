import unittest

import zope.component
import zope.interface

from Zope2.App import zcml
from Products.Five import fiveconfigure

from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso.interfaces import IWorkspaceRDFIndexer
from pmr2.virtuoso.workspace import WorkspaceRDFInfo

from pmr2.virtuoso.tests import base


class WorkspaceAnnotationTestCase(base.WorkspaceRDFTestCase):

    def test_workspace_rdf_annotation(self):
        rdfinfo = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFInfo)

        self.assertTrue(isinstance(rdfinfo, WorkspaceRDFInfo))

    def test_workspace_rdf_indexer(self):
        rdfinfo = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFInfo)

        rdfinfo.path = ['simple.rdf', 'special_cases.xml']

        indexer = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFIndexer)

        results = list(indexer.sparql_generator())
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0],
            'CLEAR GRAPH <http://nohost/plone/workspace/virtuoso_test>')

        self.assertEqual(' '.join(results[1].split()),
            u'INSERT INTO <http://nohost/plone/workspace/virtuoso_test> { '
                '<#test> <http://purl.org/dc/elements/1.1/title> "Test Node" .'
            ' }')
