import zope.component
from rdflib.graph import ConjunctiveGraph as Graph
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform import page
from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import ExposureFileViewBase

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.engine import absolute_graph

mimetype_table = {
    'xml': 'application/rdf+xml',
    'json-ld': 'application/ld+json',
}


class VirtuosoExportView(page.TraversePage):
    """
    Export all metadata associated under the context of this view that
    were previously indexed by Virtuoso.
    """

    template = ViewPageTemplateFile('virtuoso_note.pt')

    @property
    def view_url(self):
        return '%s/@@%s' % (self.context.absolute_url(), self.__name__)

    def get_graph(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        catalog = getToolByName(self.context, 'portal_catalog')
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)
        brains = catalog(path='/'.join(self.context.getPhysicalPath()))
        graph = Graph()
        for brain in brains:
            graph += absolute_graph(
                engine.get_graph_from_portal_path(brain.getPath()),
                brain.getURL(),
            )
        return graph

    def __call__(self):
        if not self.traverse_subpath:
            return super(VirtuosoExportView, self).render()
        if len(self.traverse_subpath) > 1:
            raise NotFound(self.context, self.traverse_subpath[-1])
        key = self.traverse_subpath[0]
        if not key in mimetype_table:
            raise NotFound(self.context, key)
        self.request.response.setHeader('Content-Type', mimetype_table[key])
        return self.get_graph().serialize(format=key)


class VirtuosoNoteView(VirtuosoExportView, ExposureFileViewBase):
    """
    Renders the base note.
    """

    label = 'Semantic Metadata'

    def get_graph(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)
        return absolute_graph(
            engine.get_graph(self.context),
            self.context.absolute_url(),
        )
