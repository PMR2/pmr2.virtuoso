from random import randint
import urllib
import re
from urlparse import urljoin

import rdflib
from pyparsing import ParseException
from rdflib.plugins.sparql import parser

import pmr2.rdf

iri_replacements = {
    rdflib.URIRef(''): rdflib.URIRef('#'),
}

def chunk(gen, chunk_size=100):
    try:
        while True:
            cache = []
            for _ in range(chunk_size):
                cache.append(next(gen))
            yield cache
    except StopIteration:
        if cache:
            yield cache

def quote_iri(url):
    return urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")

def n3(item):
    # handle special cases
    result = iri_replacements.get(item, item)
    if isinstance(result, rdflib.URIRef):
        result = rdflib.URIRef(quote_iri(result))
    return result.n3()

def _prefix_uri(r, prefix):
    if isinstance(r, rdflib.URIRef):
        return rdflib.URIRef(urljoin(prefix, r))
    else:
        return r

def n3_insert(graph, subject_prefix=None):
    for s, p, o in graph.triples((None, None, None)):
        if subject_prefix:
            s = _prefix_uri(s, subject_prefix)
            p = _prefix_uri(p, subject_prefix)
            o = _prefix_uri(o, subject_prefix)
        yield u'%s %s %s .' % (n3(s), n3(p), n3(o))

def insert(graph, graph_iri, subject_prefix=None, chunk_size=100):
    """
    Generate insert statements based on the graph object and iri.
    """

    for fragments in chunk(n3_insert(graph, subject_prefix), chunk_size):
        yield (
            u'INSERT INTO <%s> {\n'
            '    %s\n'
            '}' % (quote_iri(graph_iri), '\n'.join(fragments))
        )

def clear(graph_iri):
    """
    Generate a clear graph statement on the iri.
    """

    return 'CLEAR GRAPH <%s>' % (quote_iri(graph_iri))

def _add_graph_projection(statement, projection):
    return re.sub('SELECT', 'SELECT ?' + projection,
        statement, flags=re.I)

def _add_graph_graph_pattern(statement, projection):
    return re.sub('SELECT([^{]*){([^}]*)}',
        'SELECT ?%s\\1{ GRAPH ?%s {\\2} }' % (projection, projection),
        statement, flags=re.I)

def sanitize_select(statement):
    """
    Take a select statement and transform it into a select query that
    will return the graph component associated with the term.
    """

    try:
        parsed = parser.parseQuery(statement)
    except ParseException:
        return None

    part = parsed[1]['where'].get('part')
    if not part:
        # Looks like a null query, not supported.
        return None

    if len(part) > 1:
        # Multiple parts currently not supported.  If we can easily use
        # pyparsing to manipulate AND generate the result back into a
        # string this would have been trivial, but it does not do this
        # by default
        return None

    projections = {str(s['var']) for s in parsed[1]['projection']}

    if part[0].name == 'GraphGraphPattern':
        projection = str(part[0].term)
        if projection not in projections:
            # retry after adding.
            return sanitize_select(_add_graph_projection(statement,
                projection))
        # return the graph token built-in and the statement.
        return projection, statement

    projection = None
    if projection in projections:
        # just abort for now.
        return None

    projection = '_g' + str(randint(0, 100000))
    return sanitize_select(_add_graph_graph_pattern(statement, projection))
