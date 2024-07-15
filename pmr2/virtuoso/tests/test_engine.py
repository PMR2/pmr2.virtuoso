from cStringIO import StringIO
from collections import namedtuple
import unittest
from rdflib import Literal, URIRef, Graph

from pmr2.virtuoso import engine


class Engine(engine.Engine):

    def __init__(self, settings):
        self.graph_prefix = u'urn:pmr:'
        self.statements = []

    def sparql_execute(self, stmt):
        self.statements.append(stmt)


class Context(object):

    def __init__(self, path):
        self.path = path

    def getPhysicalPath(self):
        return self.path


class BaseEngineTestCase(unittest.TestCase):

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

