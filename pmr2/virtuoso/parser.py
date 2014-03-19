from cStringIO import StringIO

from lxml import etree
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
    result = Graph()
    result.parse(StringIO(rawstr), format='n3')
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
