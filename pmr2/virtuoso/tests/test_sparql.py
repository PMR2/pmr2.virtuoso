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

        result = next(sparql.insert(obj.graph,
            'http://store.example.com/metadata.rdf'))
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

        result = next(sparql.insert(obj.graph,
            'http://store.example.com/metadata.rdf'))

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

        result = next(sparql.insert(
            graph, 'http://store.example.com/metadata.rdf'))

        # Ensure that none escaped and none double escaped
        self.assertNotIn('<ha> <ha> <ha>', result)
        self.assertNotIn('\nCLEAR GRAPH <http', result)
        self.assertIn('%0ACLEAR%20GRAPH%20%3Chttp', result)

    def test_insert_chunk(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
                'data', '0', 'multi.rdf')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)

        self.assertEqual(1, len(list(sparql.insert(
            obj.graph, 'http://store.example.com/metadata.rdf'))))

        # remaining statement will be its own chunk
        self.assertEqual(2, len(list(sparql.insert(
            obj.graph, 'http://store.example.com/metadata.rdf',
            chunk_size=3))))

        # 4 statements in total
        self.assertEqual(4, len(list(sparql.insert(
            obj.graph, 'http://store.example.com/metadata.rdf',
            chunk_size=1))))

        stmts = sorted(sparql.insert(
            obj.graph, 'http://store.example.com/metadata.rdf', chunk_size=1))
        self.assertEqual(
            stmts[0], u'INSERT INTO <http://store.example.com/metadata.rdf> {'
            '\n    <#test> <http://purl.org/dc/elements/1.1/title> '
            '"Metadata File" .\n}'
        )
        self.assertEqual(
            stmts[3], u'INSERT INTO <http://store.example.com/metadata.rdf> {'
            '\n    <sibling_file#test> '
            '<http://purl.org/dc/elements/1.1/title> "Sibling File" .\n}'
        )

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

    def test_n3_insert_base_uri_object(self):
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

    def test_n3_insert_base_uri_object(self):
        obj = RdfXmlObject()
        with open(join(dirname(testing.__file__),
                'data', '0', 'nested_object.rdf')) as fd:
            rawstr = fd.read()
        obj.parse(rawstr)
        graph = sorted(sparql.n3_insert(obj.graph, 'some/data.xml'))
        self.assertEqual(graph, [
            u'<some/data.xml#inner> <http://ns.example.com/target> '
                '<http://site.example.com/target> .',
            u'<some/data.xml#inner> <http://ns.example.com/title> '
                '"Inner Title" .',
            u'<some/data.xml#root> <http://ns.example.com/is> '
                '<some/data.xml#inner> .',
        ])


class SparqlReconstructionTestCase(unittest.TestCase):

    def test_0000_expected(self):
        results = sparql.sanitize_select(
            'SELECT ?_g ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } }'
        )

        self.assertEqual(results, ('_g',
            'SELECT ?_g ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } }'
        ))

    def test_0001_simple_clean(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } }'
        )

        self.assertTrue(results[0].startswith('_g'))
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

        self.assertTrue(results[0].startswith('_g'))
        self.assertTrue(re.search(
            'SELECT \\?_g[0-9]* \\?s \\?p \\?q WHERE \\{ GRAPH \\?_g[0-9]* \\{'
            '\\?s <http://example.com/type> \\?o \\} \\}',
            results[1]
        ))

    def test_0003_dangle_fail(self):
        # Should be able to wrap the dangled patterns into its own
        # GraphGraphPattern, but limitations with rdflib and pyparsing
        # makes this rather impossible to do easily.
        results = sparql.sanitize_select(
            'SELECT ?_g ?s ?p ?q ?r ?s ?t WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } ?r ?s ?t }'
        )
        self.assertIsNone(results)

        #self.assertEqual(results, ('_g',
        #    'SELECT ?_g ?s ?p ?q WHERE { GRAPH ?_g {'
        #    '?s <http://example.com/type> ?o } }'
        #))

        results = sparql.sanitize_select(
            'SELECT ?s ?p ?q WHERE { GRAPH ?_g {'
            '?s <http://example.com/type> ?o } ?r ?s ?t }'
        )
        self.assertIsNone(results)

        #self.assertTrue(results[0].startswith('_g'))
        #self.assertTrue(re.match(
        #    'SELECT \\?_g[0-9]* \\?s \\?p \\?q WHERE { GRAPH \\?_g[0-9]* {'
        #    '\\?s <http://example.com/type> \\?o } }',
        #    results[1]
        #))

    def test_0100_limit(self):
        results = sparql.sanitize_select(
            'SELECT ?s WHERE { ?s ?p ?o } LIMIT 10'
        )
        self.assertEqual(
            results[1],
            'SELECT ?%s ?s WHERE { GRAPH ?%s { ?s ?p ?o } } LIMIT 10' % (
                results[0], results[0])
        )

    def test_0101_limit(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?o ?g WHERE { GRAPH ?g { ?s ?p ?o } } LIMIT 10'
        )
        self.assertEqual(results, (
            'g', 'SELECT ?s ?p ?o ?g WHERE { GRAPH ?g { ?s ?p ?o } } LIMIT 10'
        ))

    def test_0111_order_by(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?o ?g WHERE { GRAPH ?g { ?s ?p ?o } } ORDER BY ?s'
        )
        self.assertEqual(results, (
            'g',
            'SELECT ?s ?p ?o ?g WHERE { GRAPH ?g { ?s ?p ?o } } ORDER BY ?s'
        ))

    def test_0200_from_named(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?o ?g FROM NAMED <http://example.com/graph> '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        )
        self.assertEqual(results, (
            'g',
            'SELECT ?s ?p ?o ?g FROM NAMED <http://example.com/graph> '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        ))

    def test_0201_from_named(self):
        results = sparql.sanitize_select(
            'SELECT ?s ?p ?o ?g '
            'FROM NAMED <http://example.com/graph1> '
            'FROM NAMED <http://example.com/graph2> '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        )
        self.assertEqual(results, (
            'g',
            'SELECT ?s ?p ?o ?g '
            'FROM NAMED <http://example.com/graph1> '
            'FROM NAMED <http://example.com/graph2> '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        ))

    def test_0300_distinct(self):
        results = sparql.sanitize_select(
            'SELECT DISTINCT ?s '
            'WHERE { ?s ?p ?o }'
        )
        self.assertTrue(re.match(
            'SELECT DISTINCT \\?_g[0-9]* \\?s WHERE { GRAPH \\?_g[0-9]* { '
            '\\?s \\?p \\?o } }',
            results[1]
        ))

    def test_0301_distinct(self):
        results = sparql.sanitize_select(
            'SELECT DISTINCT ?s '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        )
        self.assertEqual(results, (
            'g',
            'SELECT DISTINCT ?g ?s '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        ))

    def test_0302_distinct(self):
        results = sparql.sanitize_select(
            'SELECT DISTINCT ?g ?s '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        )
        self.assertEqual(results, (
            'g',
            'SELECT DISTINCT ?g ?s '
            'WHERE { GRAPH ?g { ?s ?p ?o } }'
        ))

    def test_1000_union(self):
        results = sparql.sanitize_select(
            'SELECT ?s '
            'WHERE { '
            '    { ?s <http://example.com/p1> ?o } '
            '    UNION '
            '    { ?s <http://example.com/p2> ?o } '
            '}'
        )
        self.assertEqual(results[1], (
            'SELECT ?%s ?s '
            'WHERE { GRAPH ?%s { '
            '    { ?s <http://example.com/p1> ?o } '
            '    UNION '
            '    { ?s <http://example.com/p2> ?o } '
            '} }' % (results[0], results[0])
        ))

    def test_1010_union(self):
        results = sparql.sanitize_select(
            'SELECT ?s '
            'WHERE { '
            '    ?s <http://example.com/p1> ?intm . '
            '    { ?intm <http://example.com/p1> ?o } '
            '    UNION '
            '    { ?intm <http://example.com/p2> ?o } '
            '}'
        )
        self.assertEqual(results[1], (
            'SELECT ?%s ?s '
            'WHERE { GRAPH ?%s { '
            '    ?s <http://example.com/p1> ?intm . '
            '    { ?intm <http://example.com/p1> ?o } '
            '    UNION '
            '    { ?intm <http://example.com/p2> ?o } '
            '} }' % (results[0], results[0])
        ))

    def test_1011_union(self):
        results = sparql.sanitize_select(
            'SELECT ?g ?s '
            'WHERE { GRAPH ?g { '
            '    ?s <http://example.com/p1> ?intm . '
            '    { ?intm <http://example.com/p1> ?o } '
            '    UNION '
            '    { ?intm <http://example.com/p2> ?o } '
            '} }'
        )
        self.assertEqual(results, ('g',
            'SELECT ?g ?s '
            'WHERE { GRAPH ?g { '
            '    ?s <http://example.com/p1> ?intm . '
            '    { ?intm <http://example.com/p1> ?o } '
            '    UNION '
            '    { ?intm <http://example.com/p2> ?o } '
            '} }'
        ))

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
        node, result = sparql.sanitize_select(query)
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
        node, result = sparql.sanitize_select(query)
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
