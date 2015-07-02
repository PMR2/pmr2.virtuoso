import requests
import json

from zope.interface import implementer
import zope.component

from pmr2.virtuoso.sparql import quote_iri
from pmr2.virtuoso.sparql import sanitize_select
from pmr2.virtuoso.interfaces import ISparqlClient


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

    def __init__(self, portal, settings):
        self.portal = portal
        endpoint = settings.sparql_endpoint
        super(PortalSparqlClient, self).__init__(endpoint)
        self.prefix = settings.graph_prefix

    def restricted_select(self, statement):
        """
        This uses the rewrite function in the sparql module to ensure
        that the GraphGraphPattern is included and the associated term
        is part of the requested terms.
        """

        # XXX use the framework to resolve this instead?
        catalog = self.portal.portal_catalog

        q = sanitize_select(statement)

        if not q:
            # TODO come up with a meaningful way to represent errors.
            return {}

        term, stmt = q

        # if they are different then it must be sanitized.
        sanitized = statement != stmt

        results = self.query(stmt)
        # filter out all the graphs that do not match object.
        # The Virtuoso SPARQL result format follows the SPARQL 1.1
        # results JSON format as described at:
        # http://www.w3.org/TR/sparql11-results-json/

        bindings = results['results']['bindings']
        vars_ = results['head']['vars']
        def bindings_filter():
            for binding in bindings:
                g = binding.get(term, {}).get('value')
                if not g:
                    continue

                brain = catalog(path={
                    'query': g.replace(self.prefix, '', 1),
                    'depth': 0,
                })
                if not brain:
                    continue

                # replace the graph value with the public URL
                binding[term]['value'] = brain[0].getURL()

                # make new copies of everything
                yield {
                    # not quite original but...
                    'original': binding,
                    # only keep the graph value if query is not sanitized.
                    'values': [binding[v]['value'] for v in vars_
                        if not sanitized or v != term],
                    'url': binding[term]['value'],
                }

        if sanitized:
            # pop out the graph term if the query was sanitized, which
            # is always added at the beginning.
            results['head']['vars'].pop(0)
        # filtered_bindings is the key to the generator that will be
        # called to generate the results.
        results['results']['filtered_bindings'] = bindings_filter
        results['head']['graph_var'] = term
        return results
