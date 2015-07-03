from pmr2.virtuoso.client import PortalSparqlClient

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
