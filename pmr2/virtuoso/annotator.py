import zope.interface
import zope.component

from pmr2.app.factory import named_factory
from pmr2.app.annotation.interfaces import IExposureFileAnnotator
from pmr2.app.annotation.interfaces import IExposureFilePostEditAnnotator
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from pmr2.virtuoso.interfaces import IVirtuosoNote
from pmr2.virtuoso.interfaces import IExposureFileAnnotatorRDFIndexer


class VirtuosoAnnotator(ExposureFileAnnotatorBase):
    """
    Mark this file as one containing RDF that is to be exported to
    Virtuoso.
    """

    zope.interface.implements(IExposureFileAnnotator,
                              IExposureFilePostEditAnnotator)
    title = u'Export Semantic Metadata to Virtuoso'
    label = u'Semantic Metadata'
    description = u''
    for_interface = IVirtuosoNote
    edited_names = ('exclude_nav',)

    def generate(self):
        if not self.data:
            return {}
        idx = zope.component.getAdapter(self, IExposureFileAnnotatorRDFIndexer)
        idx()
        d = dict(self.data)
        self.context.setExcludeFromNav(d.get('exclude_nav'))
        return self.data

VirtuosoAnnotatorFactory = named_factory(VirtuosoAnnotator)
