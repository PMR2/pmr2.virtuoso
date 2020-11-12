import logging
import zope.interface
import zope.component

from pmr2.app.annotation.interfaces import IExposureFileAnnotator
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.exposure.interfaces import IExposureFile
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.interfaces import IExposureFileAnnotatorRDFIndexer
from pmr2.virtuoso.interfaces import IWorkspaceRDFIndexer
from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso import sparql
from pmr2.virtuoso import parser

logger = logging.getLogger(__name__)


class BaseRDFIndexer(object):
    """
    Base class for generating and inserting those triples into the
    Virtuoso RDF Store designated by the PMR2 global settings.
    """

    def __init__(self, context):
        self.context = context

    def _mk_rdfgraph(self, rdfstr):
        """
        Interim rdf grpah object generation method.
        """

        return parser.parse(rdfstr)

    def sparql_generator(self, base):
        # yields a list of statements.
        raise NotImplementedError

    def __call__(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)

        for stmt in self.sparql_generator(settings.graph_prefix):
            engine.execute('SPARQL ' + stmt)


@zope.component.adapter(IWorkspace)
@zope.interface.implementer(IWorkspaceRDFIndexer)
class WorkspaceRDFIndexer(BaseRDFIndexer):

    def sparql_generator(self, base):
        rdfinfo = zope.component.getAdapter(self.context, IWorkspaceRDFInfo)
        storage = zope.component.getAdapter(self.context, IStorage)
        full_root = base + '/'.join(self.context.getPhysicalPath())

        if len(rdfinfo.__getattribute__('__parent__').getPhysicalPath()) == 1:
            rdfinfo.__setattr__('__parent__', self.context)

        yield sparql.clear(full_root)

        for p in (rdfinfo.paths or []):
            try:
                contents = storage.file(p)
                graph = self._mk_rdfgraph(contents)
                for stmt in sparql.insert(graph, full_root, p):
                    yield stmt
            except Exception:
                logger.exception(
                    'failed to produce import statements for %s', p)


@zope.component.adapter(IExposureFileAnnotator)
@zope.interface.implementer(IExposureFileAnnotatorRDFIndexer)
class ExposureFileRDFIndexer(BaseRDFIndexer):

    def __init__(self, context):
        self.context = context

    def sparql_generator(self, base):
        # grab the file.
        full_root = base + '/'.join(self.context.context.getPhysicalPath())

        yield sparql.clear(full_root)

        graph = self._mk_rdfgraph(self.context.input)
        for stmt in sparql.insert(graph, full_root):
            yield stmt
