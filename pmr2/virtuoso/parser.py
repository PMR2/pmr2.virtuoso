from cStringIO import StringIO

from lxml import etree

from rdflib import URIRef
from rdflib.graph import Graph


upstreamneedtolearntoknowwtfisrdf = \
    'rdflibfailsathandlingrelativeurisorurnsoranything://oh/'


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
    #from rdflib.plugins.parsers import notation3
    #notation3.runNamespaceValue = ''
    #base = lambda: ''
    #notation3.base, original_base = base, notation3.base
    ## parse with our much simpler URIRef generation that doesn't mangle
    ## in the absolute file:// local path.

    #result.parse(StringIO(rawstr), format='n3')
    #result.parse(StringIO(rawstr), format='n3', publicID='#')

    result.parse(StringIO(rawstr), format='n3',
        publicID=upstreamneedtolearntoknowwtfisrdf)

    def nukeit(node):
        if not isinstance(node, URIRef):
            return node
        if node.startswith(upstreamneedtolearntoknowwtfisrdf):
            return URIRef(node.replace(upstreamneedtolearntoknowwtfisrdf, ''))
        return node
            
    real_result = Graph()
    for triple in result:
        s, p, o = triple
        if 'simple.n3' in s:
            import pdb;pdb.set_trace()
        real_result.add((nukeit(s), nukeit(p), nukeit(o)))
    return real_result
              
    ## undo our monkey patching.
    #notation3.base = original_base
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
