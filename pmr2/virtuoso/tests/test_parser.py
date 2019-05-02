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

    def test_json_ld(self):
        json_str = '''
        {
            "@context": {
                "dc": "http://purl.org/dc/terms/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            },
            "@id": "http://example.org/about",
            "dc:title": {
                "@language": "en",
                "@value": "Someone's Homepage"
            }
        }
        '''
        graph = parser.parse(json_str)
        self.assertEqual(len(list(graph)), 1)

    def test_json_ld_graph_multiple(self):
        json_str = '''
        {
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "bqbiol": "http://biomodels.net/biology-qualifiers#"
            },
            "@graph": [{
                "@id": "thing#ca",
                "bqbiol:isVersionOf": [
                    {"@id": "http://identifiers.org/obo.go/GO:0005891"}
                ]
            }, {
                "@id": "thing#na",
                "bqbiol:isVersionOf": [
                    {"@id": "http://identifiers.org/obo.go/GO:0001518"}
                ]
            }]
        }
        '''
        graph = parser.parse(json_str)
        self.assertEqual(len(list(graph)), 2)
