from cStringIO import StringIO

from lxml import etree

from rdflib import URIRef
from rdflib.graph import Graph


upstreamneedtolearntoknowwtfisiri = \
    'rdflibfailsathandlingrelativeirisorurnsoranything://oh/'


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


def parse_jsonld(rawstr):
    result = Graph()
    result.parse(data=rawstr, format='json-ld')
    return result


def parse_n3(rawstr):
    result = Graph()
    result.parse(StringIO(rawstr), format='n3',
        publicID=upstreamneedtolearntoknowwtfisiri)

    def torelative(node):
        if not isinstance(node, URIRef):
            return node
        if node.startswith(upstreamneedtolearntoknowwtfisiri):
            return URIRef(node.replace(upstreamneedtolearntoknowwtfisiri, ''))
        return node
            
    real_result = Graph()
    for triple in result:
        s, p, o = triple
        real_result.add((torelative(s), torelative(p), torelative(o)))
    return real_result


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
