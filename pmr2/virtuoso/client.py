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


def sparql_client_factory():
    """
    factory to return a SparqlClient configured for the current site.
    """

    gs = zope.component.getUtility(IPMR2GlobalSettings)
    settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
    return SparqlClient(endpoint=settings.sparql_endpoint)
