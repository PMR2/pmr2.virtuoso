import requests
import json

from zope.interface import implementer
import zope.component

from pmr2.virtuoso.sparql import quote_iri
from pmr2.virtuoso.interfaces import ISparqlClient


_base_template = """
SELECT ?_g %(query_variable)s
WHERE {
    GRAPH ?_g {
        %(triple_pattern)s
    }
}
"""


@implementer(ISparqlClient)
class SparqlClient(object):
    """
    A client for accessing the Virtuoso Sparql webservice endpoint.
    """

    def __init__(self, endpoint='http://localhost:8890/sparql',
            requests_session=None):

        if requests_session is None:
            requests_session = requests.Session()

        self.endpoint = endpoint
        self.requests_session = requests_session

    def query(self, sparql_query):
        r = self.requests_session.get(self.endpoint, params={
            'query': sparql_query,
            'format': 'application/json',
        })
        return r.json()


class PortalSparqlClient(SparqlClient):

    base_template = _base_template

    def __init__(self, portal, settings):
        self.portal = portal
        endpoint = settings.sparql_endpoint
        super(PortalSparqlClient, self).__init__(endpoint)
        self.prefix = settings.graph_prefix

    def format_query(self, query_variable, triple_pattern):
        kw = locals()
        return self.base_template % kw

    def restricted_select(self, query_variable, triple_pattern):
        """
        Very prototype, also do this using a read-only account.
        """

        # XXX use the framework to resolve this instead?
        catalog = self.portal.portal_catalog

        q = self.format_query(query_variable, triple_pattern)
        results = self.query(q)
        # filter out all the graphs that do not match object.
        # The Virtuoso SPARQL result format follows the SPARQL 1.1
        # results JSON format as described at:
        # http://www.w3.org/TR/sparql11-results-json/

        # {
        #     'head': {
        #         'links': []
        #         'vars': ['_g', ...].
        #     }
        #     'results': {
        #         'distinct': (True|False),
        #         'ordered': (True|False),
        #         'bindings': [
        #             {
        #                 '_g': {u'type': u'uri', u'value': u'http://...'},
        #                 ...
        #             },
        #             {
        #                 '_g': {u'type': u'uri', u'value': u'http://...'},
        #                 ...
        #             },
        #             ...
        #         ]
        #     }
        # }

        bindings = results['results']['bindings']
        vars_ = results['head']['vars']
        def bindings_filter():
            for binding in bindings:
                g = binding.get('_g', {}).get('value')
                if not g:
                    continue

                brain = catalog(path={
                    'query': g.replace(self.prefix, '', 1),
                    'depth': 0,
                })
                if not brain:
                    continue

                yield {
                    'original': binding,
                    'values': (binding[v]['value'] for v in vars_),
                }

        # replace bindings with the filtered version.
        results['results']['filtered_bindings'] = bindings_filter
        return results
