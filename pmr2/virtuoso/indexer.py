import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import IWorkspace, IStorage
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.interfaces import IWorkspaceRDFIndexer
from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso import sparql
from pmr2.virtuoso import parser


@zope.component.adapter(IWorkspace)
@zope.interface.implementer(IWorkspaceRDFIndexer)
class WorkspaceRDFIndexer(object):

    def __init__(self, workspace):
        self.workspace = workspace

    def _mk_rdfgraph(self, rdfstr):
        """
        Interim rdf grpah object generation method.

        Should be more agnostic, i.e. include standard/simple RDF
        serialization formats that are not XML.
        """

        return parser.parse(rdfstr)

    def sparql_generator(self, base):
        rdfinfo = zope.component.getAdapter(self.workspace, IWorkspaceRDFInfo)
        storage = zope.component.getAdapter(self.workspace, IStorage)
        full_root = base + '/'.join(self.workspace.getPhysicalPath())

        yield sparql.clear(full_root)

        for p in rdfinfo.paths:
            try:
                contents = storage.file(p)
                graph = self._mk_rdfgraph(contents)
                yield sparql.insert(graph, full_root)
            except:
                continue

    def __call__(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)

        for stmt in self.sparql_generator(settings.graph_prefix):
            engine.execute('SPARQL ' + stmt)

