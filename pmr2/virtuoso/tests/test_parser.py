import unittest

from pmr2.virtuoso import parser
from pmr2.virtuoso.tests import base


class ParserTestCase(unittest.TestCase):

    def test_simple_rdf_parse(self):
        graph = parser.parse(base.r1['simple.rdf'])
        self.assertEqual(len(list(graph)), 1)

    def test_simple_n3_parse(self):
        graph = parser.parse(base.r1['simple.n3'])
        self.assertEqual(len(list(graph)), 1)

    def test_embedded_rdf_parse(self):
        graph = parser.parse(base.r1['embedded.rdf'])
        self.assertEqual(len(list(graph)), 2)
