from cStringIO import StringIO

from lxml import etree

from rdflib import URIRef
try:
    from rdflib.graph import Graph
except ImportError:
    from rdflib.Graph import Graph


def parse_rdfxml(rawstr):
    tree = etree.parse(StringIO(rawstr))
    nodes = tree.xpath('..//rdf:RDF', namespaces={
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    })

    result = Graph()
    for node in nodes:
        s = StringIO(etree.tostring(node))
        result.parse(s, format='xml')
    return result

def parse_n3(rawstr):
    def uri(self, tok):
        return URIRef(tok)
    result = Graph()
    # monkey patching
    from rdflib.syntax.parsers.n3p.n3proc import N3Processor
    N3Processor.uri, original_uri = uri, N3Processor.uri
    # parse with our much simpler URIRef generation that doesn't mangle
    # in the absolute file:// local path.
    result.parse(StringIO(rawstr), format='n3')
    # undo our monkey patching.
    N3Processor.uri = original_uri
    return result

def parse(rawstr):
    """
    Return a rdflib.Graph object.
    """

    try:
        return parse_rdfxml(rawstr)
    except etree.XMLSyntaxError:
        pass

    return parse_n3(rawstr)
