import zope.interface
import zope.component
from zope.schema import fieldproperty

from pmr2.app.annotation.note import ExposureFileNoteBase
from pmr2.app.annotation.note import ExposureFileEditableNoteBase
from pmr2.app.annotation import note_factory

from pmr2.virtuoso.interfaces import IVirtuosoNote


class VirtuosoNote(ExposureFileNoteBase):
    """
    For storage of metadata.
    """

    zope.interface.implements(IVirtuosoNote)

    metadata = fieldproperty.FieldProperty(IVirtuosoNote['metadata'])
    exclude_nav = fieldproperty.FieldProperty(IVirtuosoNote['exclude_nav'])

VirtuosoNoteFactory = note_factory(VirtuosoNote, 'virtuoso_rdf')
