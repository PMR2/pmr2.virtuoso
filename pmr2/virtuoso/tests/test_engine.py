from cStringIO import StringIO
from collections import namedtuple
import unittest
from rdflib import Literal, URIRef, Graph

from pmr2.virtuoso import engine


class Engine(engine.Engine):

    def __init__(self, settings):
        # don't actually instantiate anything.
        self._engine = DummySQLEngine(self)
        self.graph_prefix = u'urn:pmr:'
        self.raw_source = 'fakesource'
        self.statements = []


class DummySQLEngine(object):

    def __init__(self, parent):
        self.parent = parent

    def connect(self):
        return self

    def begin(self):
        return self

    def commit(self):
        pass

    def fetchall(self):
        return []

    def execute(self, stmt):
        self.parent.statements.append(stmt)
        return self


class DummyVirtuoso(object):

    queries = []
    result = namedtuple('Result', ['graph'])

    def __init__(self, source):
        self.source = source

    def query(self, query):
        self.queries.append(query)
        return self.result(query)

    def close(self):
        pass


class Context(object):

    def __init__(self, path):
        self.path = path

    def getPhysicalPath(self):
        return self.path


class BaseEngineTestCase(unittest.TestCase):

    def setUp(self):
        self._virtuoso, engine.Virtuoso = engine.Virtuoso, DummyVirtuoso

    def tearDown(self):
        engine.Virtuoso = self._virtuoso

    def test_0000_base(self):
        engine = Engine(None)
        engine.importRdf('http://example.com/test.rdf')
        self.assertEqual(engine.statements[0],
            'sparql load <http://example.com/test.rdf> into graph '
            '<urn:example:pmr2.virtuoso>')

    def test_0000_base(self):
        engine = Engine(None)
        engine.importRdf('http://example.com/test.rdf',
            'http://graph.example.com/')
        self.assertEqual(engine.statements[0],
            'sparql load <http://example.com/test.rdf> into graph '
            '<http://graph.example.com/>')

    def test_0010_multile_hostile(self):
        engine = Engine(None)
        engine.bulkImportRdf([
            'http://example.com/test.rdf',
            'http://example.com/test.rdf?parma=12?pwn"> into graph ',
        ], graph='urn:example:pmr2.virtuoso')
        self.assertEqual(engine.statements, [
            'sparql load <http://example.com/test.rdf> into graph '
            '<urn:example:pmr2.virtuoso>',
            'sparql load <http://example.com/test.rdf%3Fparma%3D12?'
            'pwn%22%3E+into+graph+> into graph <urn:example:pmr2.virtuoso>',
        ])

    def test_0100_get_graph(self):
        engine = Engine(None)
        context = Context(['', 'path', 'to', 'object'])
        result = engine.get_graph(context)
        # The fake mock is set up to return the query is as.
        self.assertEqual(
            result,
            u'CONSTRUCT { ?s ?p ?o } FROM <urn:pmr:/path/to/object> '
            'WHERE { ?s ?p ?o }'
        )

    def test_9000_absolute_iri(self):
        literal = Literal(u'a literal')
        self.assertIs(
            engine.absolute_iri(literal, 'http://example.com'), literal)
        self.assertEqual(str(engine.absolute_iri(
            URIRef('http://standard.example.com/some/resource'),
            'http://alt.example.com/',
        )), 'http://standard.example.com/some/resource')
        self.assertEqual(str(engine.absolute_iri(
            URIRef('./random/resource'),
            'http://base.example.com/some/path',
        )), 'http://base.example.com/some/random/resource')

    def test_9100_absolute_graph(self):
        graph = Graph()
        graph.add([
            URIRef(u'./random/resource'),
            URIRef(u'http://namespace.example.com/some/predicate'),
            Literal(u'a literal')
        ])
        new_graph = engine.absolute_graph(
            graph, u'http://example.com/path/metadata.rdf')
        self.assertEqual(list(new_graph)[0], (
            URIRef(u'http://example.com/path/random/resource'),
            URIRef(u'http://namespace.example.com/some/predicate'),
            Literal(u'a literal')
        ))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseEngineTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

