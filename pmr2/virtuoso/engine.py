import logging
from contextlib import contextmanager
from urlparse import urljoin

import sqlalchemy
from sqlalchemy.sql import bindparam
from sqlalchemy.exc import ResourceClosedError

from rdflib.graph import ConjunctiveGraph as Graph
from rdflib.store import Store
from rdflib.plugin import get as plugin
from rdflib.term import URIRef

import zope.component
import zope.interface

from Products.CMFCore.utils import getToolByName

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.helper import quote_url

Virtuoso = plugin("Virtuoso", Store)

logger = logging.getLogger('pmr2.virtuoso.engine')
# disable connection logging of credentials at INFO level
logging.getLogger('virtuoso.vstore').setLevel(logging.WARNING)


class Engine(object):
    """
    SQL Alchemy engine adapter helper class
    """

    zope.interface.implements(IEngine)

    def __init__(self, settings):
        source = settings.source
        self.raw_source = settings.raw_source
        self.graph_prefix = settings.graph_prefix
        self._engine = sqlalchemy.create_engine(source)

    def importRdf(self, url, graph=None):
        conn = self._engine.connect()
        trans = conn.begin()

        sqltmpl = 'sparql load <%(source)s>'
        params = {'source': quote_url(url)}
        if graph:
            sqltmpl = 'sparql load <%(source)s> into graph <%(graph)s>'
            params['graph'] = quote_url(graph)

        sqlstr = sqltmpl % params

        try:
            lr = conn.execute(sqlstr)
            fa = lr.fetchall()
            # assuming the results is in this format.
            results = [r.values()[0] for r in fa]
            lr.close()
        except:
            logger.error('fail to execute sql', exc_info=1)
        trans.commit()
        return results

    def bulkImportRdf(self, urls, graph=None):
        results = []
        engine = self._engine
        for source in urls:
            r = self.importRdf(source, graph)
            results.extend(r)
        return results

    def execute(self, stmt):
        conn = self._engine.connect()
        trans = conn.begin()

        try:
            lr = conn.execute(stmt)
            try:
                fa = lr.fetchall()
            except ResourceClosedError:
                results = []
            else:
                # assuming the results is in this format.
                results = [r.values() for r in fa]
            lr.close()
        except Exception:
            logger.error('fail to execute sql', exc_info=1)
        else:
            trans.commit()
            return results
        return ['# check logs for errors']

    @contextmanager
    def virtuoso_store(self):
        """
        Access the raw virtuoso store via rdflib

        This is managed via a context manager to better ensure that the
        store is closed when usage is done, as leaving this open can
        lock the server from other attempts to access.
        """

        store = Virtuoso(self.raw_source)
        try:
            yield store
        finally:
            store.close()

    def get_graph_from_portal_path(self, path):
        """
        Return a rdflib.Graph from virtuoso using the provided path to an
        object that was indexed previously.
        """

        full_root = self.graph_prefix + path
        with self.virtuoso_store() as store:
            results = store.query(
                u'CONSTRUCT { ?s ?p ?o } FROM <%s> WHERE { ?s ?p ?o }' % (
                    full_root
                )
            )

        return results.graph

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
