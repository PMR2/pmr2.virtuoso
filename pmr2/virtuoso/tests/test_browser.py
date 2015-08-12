import json
import unittest
import urllib
from cStringIO import StringIO

import zope.component
from plone.testing.z2 import Browser

from Products.CMFCore.utils import getToolByName

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.browser.client import SparqlClientForm
from pmr2.virtuoso.interfaces import ISparqlClient
from pmr2.virtuoso.interfaces import ISettings
from pmr2.virtuoso.testing.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER


class ClientBrowserTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['portal'].REQUEST

        self.testbrowser = Browser(self.layer['portal'])

    def publish(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wft = getToolByName(self.portal, 'portal_workflow')
        wft.setDefaultChain("simple_publication_workflow")
        try:
            wft.doActionFor(self.portal.workspace.virtuoso_test, 'publish')
            setRoles(self.portal, TEST_USER_ID, ['Member'])
            # Force a commit to make things work.
            self.portal.workspace.virtuoso_test.reindexObject()
            import transaction
            transaction.commit()
        except:
            # something went wrong because the plone/zope test layers
            # implemented in a very fubar'd way but we don't care.
            pass

    def test_0000_form_render(self):
        form = SparqlClientForm(self.portal, self.request)
        results = form()
        self.assertIn('Execute', results)

    def test_0100_form_submit(self):
        # doesn't matter what these are, as we use dummy values, as long
        # as the graph var is determined.
        self.request.form['form.widgets.query'] = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.request.form['form.buttons.execute'] = 1
        self.request.method = 'POST'
        form = SparqlClientForm(self.portal, self.request)
        form.disableAuthenticator = True
        results = form()
        self.assertEqual(
            len(results.split('http://nohost/plone/workspace/virtuoso_test')),
            5) # 4 of these in total.
        self.assertIn('http://example.com/object', results)
        self.assertNotIn('urn:pmr:virtuoso:/plone/workspace/no_permission',
            results)

    def test_0101_browser_submit_noperm(self):
        portal_url = self.portal.absolute_url()
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search')
        self.testbrowser.getControl(name='form.widgets.query').value = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.testbrowser.getControl(name='form.buttons.execute').click()
        results = self.testbrowser.contents
        self.assertEqual(
            len(results.split('http://nohost/plone/workspace/virtuoso_test')),
            1) # nothing for now, no permission

    def test_0102_browser_submit(self):
        self.publish()
        portal_url = self.portal.absolute_url()
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search')
        self.testbrowser.getControl(name='form.widgets.query').value = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.testbrowser.getControl(name='form.buttons.execute').click()
        results = self.testbrowser.contents
        self.assertEqual(
            len(results.split('http://nohost/plone/workspace/virtuoso_test')),
            5)
        self.assertIn('http://example.com/object', results)
        self.assertNotIn('urn:pmr:virtuoso:/plone/workspace/no_permission',
            results)

    def test_0150_bad_sparql(self):
        self.publish()
        portal_url = self.portal.absolute_url()
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search')
        self.testbrowser.getControl(name='form.widgets.query').value = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o }'
        self.testbrowser.getControl(name='form.buttons.execute').click()
        results = self.testbrowser.contents
        self.assertIn('<dt>Error</dt>', results)

    def test_1000_form_submit_mime_query(self):
        self.publish()
        portal_url = self.portal.absolute_url()
        self.testbrowser.addHeader('Accept', 'application/sparql-results+json')
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search?query=' +
            urllib.quote(
                'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'))
        results = self.testbrowser.contents
        jr = json.loads(results)  # is JSON
        self.assertEqual(jr, {"head": {"link": [], "vars": ["_g", "o"]},
            "results": {"ordered": True, "distinct": False, "bindings": [
                {"_g": {"type": "uri",
                    "value": "http://nohost/plone/workspace/virtuoso_test"},
                    "o": {"type": "uri", "value": "http://example.com/object"}},
                {"_g": {"type": "uri",
                    "value": "http://nohost/plone/workspace/virtuoso_test"},
                    "o": {"type": "uri", "value": "test.cfg#left"}}
            ],
        }})

    def test_1001_form_submit_mime_stdin(self):
        self.publish()
        portal_url = self.portal.absolute_url()
        self.testbrowser.addHeader('Accept', 'application/sparql-results+json')
        data = 'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search', data)
        results = self.testbrowser.contents
        jr = json.loads(results)  # is JSON
        self.assertEqual(jr, {"head": {"link": [], "vars": ["_g", "o"]},
            "results": {"ordered": True, "distinct": False, "bindings": [
                {"_g": {"type": "uri",
                    "value": "http://nohost/plone/workspace/virtuoso_test"},
                    "o": {"type": "uri", "value": "http://example.com/object"}},
                {"_g": {"type": "uri",
                    "value": "http://nohost/plone/workspace/virtuoso_test"},
                    "o": {"type": "uri", "value": "test.cfg#left"}}
            ],
        }})

    def test_1500_error_handling(self):
        self.publish()
        portal_url = self.portal.absolute_url()
        self.testbrowser.addHeader('Accept', 'application/sparql-results+json')
        data = 'SELECT ?_g ?s ?p ?o WHERE GRAPH ?_g { ?s ?p ?o } }'
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search', data)
        results = self.testbrowser.contents
        jr = json.loads(results)  # is JSON
        self.assertEqual(jr, {"error": "invalid SPARQL query"})
