import unittest
import json
from cStringIO import StringIO

import zope.component

from Products.PloneTestCase import ptc

from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso.testing.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER

try:
    from pmr2.virtuoso.browser import collection
    from pmr2.json.tests import base
    _pmr2_json_collection = True
except ImportError:
    _pmr2_json_collection = False
_pmr2_json_collection = True


@unittest.skipUnless(_pmr2_json_collection, 'pmr2.json is unavailable')
class VirtuosoTestCase(unittest.TestCase):
    """
    Testing functionalities of forms that don't fit well into doctests.
    """

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def test_base_render(self):
        request = base.TestRequest()
        context = self.layer['portal'].workspace['virtuoso_test']
        f = collection.WorkspaceRDFInfoEditForm(context, request)
        results = json.loads(f())
        self.assertEqual(
            [i['name'] for i in results['collection']['template']['data']],
            [u'form.widgets.paths', u'form.buttons.apply',
                u'form.buttons.export_rdf']
        )
        self.assertEqual(len(
            results['collection']['template']['data'][0]['options']), 8)

    def test_workspace_rdf_edit_form_submit(self):
        context = self.layer['portal'].workspace['virtuoso_test']
        request = base.TestRequest(method='POST',
            stdin=StringIO('{"template": {"data": ['
                '{"name": "form.widgets.paths", "value": ["simple.rdf"]},'
                '{"name": "form.buttons.apply", "value": 1}'
            ']}}'))
        form = collection.WorkspaceRDFInfoEditForm(context, request)
        result = json.loads(form())
        self.assertEqual(result['collection']['template']['data'][0]['value'],
            ['simple.rdf'])
        rdfinfo = zope.component.getAdapter(context, IWorkspaceRDFInfo)

        self.assertEqual(rdfinfo.paths, ['simple.rdf'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(VirtuosoTestCase))
    return suite
