import unittest

import zope.component
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.client import PortalSparqlClient
from pmr2.virtuoso.browser.client import SparqlClientForm
from pmr2.virtuoso.interfaces import ISparqlClient
from pmr2.virtuoso.interfaces import ISettings
from pmr2.virtuoso.tests.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER

dummy_response = {
    u'head': {
        u'link': [],
        u'vars': [u'_g', u'o']
    },
    u'results': {
        u'distinct': False,
        u'ordered': True,
        u'bindings': [
            {u'_g': {u'type': u'uri',
                u'value': u'urn:pmr:virtuoso:/plone/workspace/virtuoso_test'},
             u'o': {u'type': u'uri', u'value': u'http://example.com/object'}},
            {u'_g': {u'type': u'uri',
                u'value': u'urn:pmr:virtuoso:/plone/workspace/virtuoso_test'},
             u'o': {u'type': u'uri', u'value': u'test.cfg#left'}},
            {u'_g': {u'type': u'uri',
                u'value': u'urn:pmr:virtuoso:/plone/workspace/no_permission'},
             u'o': {u'type': u'uri', u'value': u'http://example.com/object'}},
        ],
    }
}

class DummyPortalSparqlClient(PortalSparqlClient):

    def query(self, sparql_query):
        return dummy_response


class ClientBrowserTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['portal'].REQUEST
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        self.settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        sm = zope.component.hooks.getSiteManager()
        sm.registerAdapter(DummyPortalSparqlClient,
            (IPloneSiteRoot, ISettings), ISparqlClient)

    def tearDown(self):
        pass

    def test_0000_form_render(self):
        form = SparqlClientForm(self.portal, self.request)
        results = form()
        self.assertIn('Execute', results)

    def test_0100_form_submit(self):
        # doesn't matter what these are, as we use dummy values, as long
        # as the graph var is determined.
        self.request.form['form.widgets.statement'] = \
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

    def test_1000_form_submit_mime(self):
        portal_url = self.portal.absolute_url()
        #self.testbrowser.addHeader('Accept', 'application/sparql-results+json')
        #self.testbrowser.open(portal_url + '/pmr2_virtuoso_search')
