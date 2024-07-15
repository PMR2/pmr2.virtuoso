import logging
from contextlib import contextmanager
from urlparse import urljoin

from rdflib.graph import ConjunctiveGraph as Graph
from rdflib.store import Store
from rdflib.term import URIRef
import requests

import zope.component
import zope.interface

from Products.CMFCore.utils import getToolByName

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.helper import quote_url

logger = logging.getLogger('pmr2.virtuoso.engine')
# disable connection logging of credentials at INFO level
logging.getLogger('virtuoso.vstore').setLevel(logging.WARNING)


class Engine(object):
    """
    SQL Alchemy engine adapter helper class
    """

    zope.interface.implements(IEngine)

    def __init__(self, settings):
        # XXX assumes virtuoso, and has auth endpoint with this suffix
        self.sparql_endpoint = settings.sparql_endpoint + '-auth'
        self.requests_auth = settings.requests_auth
        self.graph_prefix = settings.graph_prefix

    def sparql_execute(self, stmt, mimetype='application/rdf+xml'):
        session = requests.Session()
        session.auth = self.requests_auth
        r = session.post(self.sparql_endpoint, data={
            'query': stmt,
            'format': mimetype,
        })
        if r.status_code == 200:
            return r.text

        if r.status_code == 401:
            logger.warn("Virtuoso SPARQL endpoint auth error")
        elif r.status_code == 400:
            logger.info("Virtuoso SPARQL execution error: %s", r.text)
            logger.debug("error executing statement: %r", stmt)
        else:
            logger.warn(
                "Virtuoso SPARQL endpoint unexpected HTTP error code: %s",
                r.status_code
            )

        return None

    def get_graph_from_portal_path(self, path):
        """
        Return a rdflib.Graph from virtuoso using the provided path to an
        object that was indexed previously.
        """

        full_root = self.graph_prefix + path
        rdfxml = self.sparql_execute(
            u'CONSTRUCT { ?s ?p ?o } FROM <%s> WHERE { ?s ?p ?o }' % (
                full_root
            )
        )
        graph = Graph()
        graph.parse(data=rdfxml)
        return graph

    def get_graph(self, context):
        """
        Return a rdflib.Graph from virtuoso from the provided context
        object provided by the portal.
        """

        return self.get_graph_from_portal_path(
            '/'.join(context.getPhysicalPath()))


def absolute_iri(iri, base):
    """
    Produce an absolute IRI from the given base.
    """

    if not isinstance(iri, URIRef):
        return iri
    return URIRef(urljoin(base, str(iri)))


def absolute_graph(source_graph, base):
    """
    Given the graph and a base IRI, join all relative IRIs to the base
    IRI found in the graph.
    """

    graph = Graph()
    for triple in source_graph:
        graph.add([absolute_iri(item, base) for item in triple])
    return graph
