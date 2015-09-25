import re
import unittest
from os.path import dirname, join

from pmr2.rdf.base import RdfXmlObject
from pmr2.virtuoso import parser
from pmr2.virtuoso import sparql
from pmr2.virtuoso import testing


class SparqlTestCase(unittest.TestCase):

    def test_quote(self):
        # sparql injection is bad.
        self.assertEqual(sparql.quote_iri('<>'), '%3C%3E')
        self.assertEqual(sparql.quote_iri('""'), '%22%22')

    def test_insert_special(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
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
        # Strings properly escaped in a string
        self.assertIn('"Title \\"}<for> an external resource."', result)
        # Backslashes in URLs should be escaped
        self.assertNotIn('.\\file#test', result)
        self.assertIn('.%5Cfile#test', result)

    def test_iri_escape(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
                'data', '0', 'injection.rdf')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)

        result = sparql.insert(obj.graph,
            'http://store.example.com/metadata.rdf')

        # all < and > needs to be escaped
        self.assertNotIn('<ha> <ha> <ha>', result)
        # all whitespaces escaped in iri
        self.assertNotIn('\nCLEAR GRAPH <http', result)
        self.assertIn('%0ACLEAR%20GRAPH%20%3Chttp', result)

    def test_iri_escape_n3(self):
        with open(join(dirname(testing.__file__),
                'data', '0', 'complex.n3')) as fd:
            rawstr = fd.read()
        graph = parser.parse(rawstr)

        result = sparql.insert(graph, 'http://store.example.com/metadata.rdf')

        # Ensure that none escaped and none double escaped
        self.assertNotIn('<ha> <ha> <ha>', result)
        self.assertNotIn('\nCLEAR GRAPH <http', result)
        self.assertIn('%0ACLEAR%20GRAPH%20%3Chttp', result)

    def test_clear(self):
        result = sparql.clear('http://store.example.com/metadata.rdf')
        self.assertEqual(result,
            'CLEAR GRAPH <http://store.example.com/metadata.rdf>')

        result = sparql.clear('<>')
        self.assertEqual(result, 'CLEAR GRAPH <%3C%3E>')

    def test_n3_insert(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
                'data', '0', 'multi.rdf')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)
        graph = sorted(sparql.n3_insert(obj.graph))

        self.assertEqual(graph, [
            u'<#test> <http://purl.org/dc/elements/1.1/title> '
                '"Metadata File" .',
            u'<../parent/file#test> <http://purl.org/dc/elements/1.1/title> '
                '"Parent File" .',
            u'<nested/file#test> <http://purl.org/dc/elements/1.1/title> '
                '"Nested File" .',
            u'<sibling_file#test> <http://purl.org/dc/elements/1.1/title> '
                '"Sibling File" .',
        ])

    def test_n3_insert_base(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
                'data', '0', 'multi.rdf')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)
        graph = sorted(sparql.n3_insert(obj.graph, 'metadata.rdf'))

        # the <#test> should have been normalized.
        self.assertEqual(graph, [
            u'<../parent/file#test> <http://purl.org/dc/elements/1.1/title> '
                '"Parent File" .',
            u'<metadata.rdf#test> <http://purl.org/dc/elements/1.1/title> '
                '"Metadata File" .',
            u'<nested/file#test> <http://purl.org/dc/elements/1.1/title> '
                '"Nested File" .',
            u'<sibling_file#test> <http://purl.org/dc/elements/1.1/title> '
                '"Sibling File" .',
        ])

    def test_n3_insert_nested_path(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
                'data', '0', 'multi.rdf')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)
        graph = sorted(sparql.n3_insert(obj.graph, 'multi/path/metadata.xml'))
        self.assertEqual(graph, [
            u'<multi/parent/file#test> '
                '<http://purl.org/dc/elements/1.1/title> "Parent File" .',
            u'<multi/path/metadata.xml#test> '
                '<http://purl.org/dc/elements/1.1/title> "Metadata File" .',
            u'<multi/path/nested/file#test> '
                '<http://purl.org/dc/elements/1.1/title> "Nested File" .',
            u'<multi/path/sibling_file#test> '
                '<http://purl.org/dc/elements/1.1/title> "Sibling File" .',
        ])


class SparqlReconstructionTestCase(unittest.TestCase):

    def assertDefaultProjections(self, results):
        # this may need to be made more robust.
        projections = results[0]
        for p in projections:
            self.assertTrue(p.startswith('_g'))

    def test_0000_expected(self):
        results = sparql.sanitize_select(
            'SELECT ?_g ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } }'
        )

        self.assertEqual(results, (['_g'],
            'SELECT ?_g ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } }'
        ))

    def test_0001_simple_clean(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } }'
        )

        self.assertDefaultProjections(results)
        self.assertTrue(re.match(
            'SELECT \\?_g[0-9]* \\?s \\?p \\?q WHERE { GRAPH \\?_g[0-9]* {'
            '\\?s <http://example.com/type> \\?o } }',
            results[1]
        ))

    def test_0002_complete_clean(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE {'
            '?s <http://example.com/type> ?o }'
        )

        self.assertDefaultProjections(results)
        self.assertTrue(re.search(
            'SELECT \\?_g[0-9]* \\?s \\?p \\?q WHERE \\{ GRAPH \\?_g[0-9]* \\{'
            '\\?s <http://example.com/type> \\?o \\} \\}',
            results[1]
        ))

    def test_0003_dangled_section(self):
        projections, result = sparql.sanitize_select(
            'SELECT ?_g ?s ?p ?q ?r ?s ?t WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } ?r ?s ?t }'
        )

        self.assertEqual(len(projections), 2)
        self.assertDefaultProjections(results)

        self.assertEqual(re.match(
            'SELECT \\?_g \\?_g[0-9]* \\?s \\?p \\?q WHERE \\{ GRAPH \\?_g \\{'
            '\\?s <http://example.com/type> \\?o \\} GRAPH \\?_g[0-9]* \\{'
            '?r ?s ?t \\} \\}'
        ))

    def test_0004_multi_graph(self):
        # a valid multiple GraphGraphPattern query
        q = ('SELECT ?_g ?_h ?s ?o ?t ?u WHERE { '
                'GRAPH ?_g { '
                    '?s <http://example.com/type> ?o '
                '} '
                'GRAPH ?_h { ?s ?t ?u } '
            '}')
        projections, result = sparql.sanitize_select(q)

        # valid queries don't change, but projections captured
        self.assertEqual(projections, ['?_g', '?_h'])
        self.assertEqual(result, q)

    def test_7000_chained(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE { ?s <http://example.com/type> ?o };'
            'SELECT ?s ?p ?q WHERE { ?s <http://example.com/type> ?o }'
        )
        self.assertIsNone(results)

    def test_8000_not_select(self):
        self.assertIsNone(sparql.sanitize_select(
            'CLEAR GRAPH <http://example.com/graph>'
        ))

    def test_9000_invalid(self):
        self.assertIsNone(sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE {'
            '?s <http://example.com/type> ?o '
        ))
        self.assertIsNone(sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE '
            '?s <http://example.com/type> ?o }'
        ))
        self.assertIsNone(sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE {'
            '?s http://example.com/type> ?o >'
        ))

    def test_5000_multiline(self):
        query = (
            'SELECT ?me\n'
            'WHERE { \n'
            '?me <http://www.obofoundry.org/ro/ro.owl#located_in> '
                '<http://identifiers.org/fma/FMA:17693> \n'
            '}\n'
        )
        projections, result = sparql.sanitize_select(query)
        self.assertTrue(result.startswith('SELECT ?_g'))
        self.assertTrue('GRAPH' in result)
        self.assertTrue(result.endswith('{ \n'
            '?me <http://www.obofoundry.org/ro/ro.owl#located_in> '
            '<http://identifiers.org/fma/FMA:17693> \n'
            '} }\n'
        ))

    def test_5001_multiline_with_prefix(self):
        query = (
            'PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>\n'
            'PREFIX fma: <http://identifiers.org/fma/>\n'
            '\n'
            'SELECT ?me\n'
            'WHERE {\n'
            '    ?me ro:located_in fma:FMA:17693\n'
            '}\n'
        )
        projections, result = sparql.sanitize_select(query)
        self.assertTrue(result.startswith(
            'PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>\n'
            'PREFIX fma: <http://identifiers.org/fma/>\n'
            '\n'
            'SELECT ?_g'
        ))
        self.assertTrue('GRAPH' in result)
        self.assertTrue(result.endswith('{\n'
            '    ?me ro:located_in fma:FMA:17693\n'
            '} }\n'
        ))
