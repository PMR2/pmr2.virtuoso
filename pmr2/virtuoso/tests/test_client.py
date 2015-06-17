import unittest

import zope.component

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso import engine
from pmr2.virtuoso.interfaces import ISparqlClient
from pmr2.virtuoso.tests.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER


class ClientTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        self.settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')

    def tearDown(self):
        pass

    def test_0000_base(self):
        self.settings.sparql_endpoint = u'http://nohost/sparql'
        client = zope.component.getMultiAdapter((self.portal, self.settings),
            ISparqlClient)
        self.assertEqual(client.portal, self.portal)
        self.assertEqual(client.endpoint, u'http://nohost/sparql')

    def test_0001_query_construction(self):
        client = zope.component.getMultiAdapter((self.portal, self.settings),
            ISparqlClient)
        q = client.format_query('?s ?p ?o', '?s ?p ?o').strip()
        self.assertEqual(q, ''
            'SELECT ?_g ?s ?p ?o\n'
            'WHERE {\n'
            '    GRAPH ?_g {\n'
            '        ?s ?p ?o\n'
            '    }\n'
            '}'
        )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ClientTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

