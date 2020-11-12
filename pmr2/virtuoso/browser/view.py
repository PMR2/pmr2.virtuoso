import zope.component
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import NotFound

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import ExposureFileViewBase

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.engine import absolute_graph

mimetype_table = {
    'xml': 'application/rdf+xml',
    'json-ld': 'application/ld+json',
}


class VirtuosoNoteView(ExposureFileViewBase):
    """
    Renders the base note.
    """

    template = ViewPageTemplateFile('virtuoso_note.pt')
    label = 'Semantic Metadata'

    def get_graph(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)
        return engine.get_graph(self.context)

    def __call__(self):
        if not self.traverse_subpath:
            return super(VirtuosoNoteView, self).render()
        if len(self.traverse_subpath) > 1:
            raise NotFound(self.context, self.traverse_subpath[-1])
        key = self.traverse_subpath[0]
        if not key in mimetype_table:
            raise NotFound(self.context, key)
        graph = absolute_graph(self.get_graph(), self.context.absolute_url())
        self.request.response.setHeader('Content-Type', mimetype_table[key])
        return graph.serialize(format=key)
