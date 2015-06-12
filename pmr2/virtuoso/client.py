import requests
import json

from zope.interface import implementer
import zope.component

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.sparql import quote_iri
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


# I hate naming things, this is a bad name.
class SettingsSparqlClient(SparqlClient):

    base_template = """
    SELECT ?_g %(query_variable)s
    WHERE {
        GRAPH ?_g {
            %(triple_pattern)s
        }
    }
    """

    def __init__(self, settings):
        endpoint = settings.sparql_endpoint
        super(SettingsSparqlClient, self).__init__(endpoint)
        self.prefix = settings.graph_prefix

    def format_query(self, query_variable, triple_pattern):
        kw = locals()
        return self.base_template % kw

    def restricted_select(self, query_variable, triple_pattern):
        """
        Very prototype, also do this using a read-only account.
        """

        q = self.format_query(query_variable, triple_pattern)
        results = self.query(q)
        # filter out all the graphs that do not match object.
        return results
