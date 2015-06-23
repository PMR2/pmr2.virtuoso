from os.path import join, dirname
import unittest

from pmr2.virtuoso import parser


class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.r1 = {}
        for fn in ['simple.n3', 'simple.rdf', 'embedded.rdf']:
            with open(join(dirname(__file__), 'data', '0', fn)) as fd:
                self.r1[fn] = fd.read()

    def test_simple_rdf_parse(self):
        graph = parser.parse(self.r1['simple.rdf'])
        self.assertEqual(len(list(graph)), 1)

    def test_simple_n3_parse(self):
        graph = parser.parse(self.r1['simple.n3'])
        self.assertEqual(len(list(graph)), 2)

    def test_embedded_rdf_parse(self):
        graph = parser.parse(self.r1['embedded.rdf'])
        self.assertEqual(len(list(graph)), 2)
