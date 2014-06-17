import unittest
from os.path import dirname, join

from pmr2.rdf.base import RdfXmlObject
from pmr2.virtuoso import sparql


class SparqlTestCase(unittest.TestCase):

    def test_quote(self):
        # sparql injection is bad.
        self.assertEqual(sparql.quote_iri('<>'), '%3C%3E')
        self.assertEqual(sparql.quote_iri('""'), '%22%22')

    def test_insert_special(self):
        obj = RdfXmlObject()
        with open(join(dirname(__file__),
                'data', '0', 'special_cases.xml')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)

        result = sparql.insert(obj.graph,
            'http://store.example.com/metadata.rdf')
        self.assertTrue(result.startswith('INSERT'))
        # blank IRI are converted into the <#> form
        self.assertNotIn('<> ', result)
        # but the ones inside strings shouldn't be touched.
        self.assertIn('<><>', result)

    def test_clear(self):
        result = sparql.clear('http://store.example.com/metadata.rdf')
        self.assertEqual(result,
            'CLEAR GRAPH <http://store.example.com/metadata.rdf>')

        result = sparql.clear('<>')
        self.assertEqual(result, 'CLEAR GRAPH <%3C%3E>')
