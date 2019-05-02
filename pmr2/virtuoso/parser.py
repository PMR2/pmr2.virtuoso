from cStringIO import StringIO

from lxml import etree

from rdflib import URIRef
from rdflib.graph import Graph
from rdflib.graph import ConjunctiveGraph

import urlparse

# force urljoin to behave correctly
urlparse.uses_relative.append('jsonld')
urlparse.uses_netloc.append('jsonld')

# in theory, both of these prefix are the same but they are mishandled/
# mismanaged in their own hilariously broken ways, so going to leave
# them as is.
n3_prefix = 'rdflibfailsathandlingrelativeirisorurnsoranything://oh/'
json_ld_prefix = 'jsonld://rdflib_prefix/'


def parse_rdfxml(rawstr):
    tree = etree.parse(StringIO(rawstr))
    nodes = tree.xpath('..//rdf:RDF', namespaces={
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    })

    result = Graph()
    for node in nodes:
        result.parse(data=etree.tostring(node), format='xml')
    return result


def fix_relative_uriref(graph, fake_prefix):
    def torelative(node):
        if not isinstance(node, URIRef):
            return node
        if node.startswith(fake_prefix):
            return URIRef(node.replace(fake_prefix, ''))
        return node
            
    corrected_graph = Graph()
    for triple in graph:
        s, p, o = triple
        corrected_graph.add((torelative(s), torelative(p), torelative(o)))
    return corrected_graph


def parse_jsonld(rawstr):
    result = ConjunctiveGraph()
    result.parse(data=rawstr, format='json-ld', base=json_ld_prefix)
    return fix_relative_uriref(result, json_ld_prefix)


def parse_n3(rawstr):
    result = Graph()
    result.parse(data=rawstr, format='n3', publicID=n3_prefix)
    return fix_relative_uriref(result, n3_prefix)


def parse(rawstr):
    """
    Return a rdflib.Graph object.
    """

    try:
        return parse_rdfxml(rawstr)
    except etree.XMLSyntaxError:
        pass

    if rawstr.lstrip()[:1] == '{':
        return parse_jsonld(rawstr)
    else:
        return parse_n3(rawstr)
