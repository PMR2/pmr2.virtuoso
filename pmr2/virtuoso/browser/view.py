import zope.component
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import NotFound

from pmr2.app.workspace.browser.browser import WorkspaceRawfileXmlBase
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import ExposureFileViewBase

from pmr2.annotation.shjs.browser import SourceTextNote


class VirtuosoNoteView(ExposureFileViewBase):
    """
    Renders the base note.
    """

    template = ViewPageTemplateFile('virtuoso_note.pt')
    label = 'Semantic Metadata'
