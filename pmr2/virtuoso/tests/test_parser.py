from os.path import join, dirname
import unittest

from pmr2.virtuoso import parser
from pmr2.virtuoso import testing


class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.r1 = {}
        for fn in ['simple.n3', 'simple.rdf', 'embedded.rdf', 'turtle.ttl']:
            with open(join(dirname(testing.__file__), 'data', '0', fn)) as fd:
                self.r1[fn] = fd.read()

    def test_simple_rdf_parse(self):
        graph = parser.parse(self.r1['simple.rdf'])
        self.assertEqual(len(list(graph)), 1)

    def test_simple_n3_parse(self):
        graph = parser.parse(self.r1['simple.n3'])
        self.assertEqual(len(list(graph)), 2)

    def test_simple_turtle_parse(self):
        graph = parser.parse(self.r1['turtle.ttl'])
        self.assertEqual(len(list(graph)), 14)

    def test_embedded_rdf_parse(self):
        graph = parser.parse(self.r1['embedded.rdf'])
        self.assertEqual(len(list(graph)), 2)
