import zope.interface
import zope.component

from pmr2.app.factory import named_factory
from pmr2.app.annotation.interfaces import IExposureFileAnnotator
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from pmr2.virtuoso.interfaces import IVirtuosoNote
from pmr2.virtuoso.interfaces import IExposureFileAnnotatorRDFIndexer


class VirtuosoAnnotator(ExposureFileAnnotatorBase):
    """
    Mark this file as one containing RDF that is to be exported to
    Virtuoso.
    """

    zope.interface.implements(IExposureFileAnnotator)
    title = u'Export Semantic Metadata to Virtuoso'
    label = u'Semantic Metadata'
    description = u''
    for_interface = IVirtuosoNote

    def generate(self):
        idx = zope.component.getAdapter(self, IExposureFileAnnotatorRDFIndexer)
        idx()
        return (
            # temporary placeholder values.
            ('metadata', u''),
        )

VirtuosoAnnotatorFactory = named_factory(VirtuosoAnnotator)
