from zope.interface import implementer
from zope.component import getAdapter
from pmr2.app.exposure.interfaces import IExposureFileTool
from pmr2.app.exposure.interfaces import IExposureSourceAdapter


@implementer(IExposureFileTool)
class VirtuosoExport(object):
    """
    Link to the export page.
    """

    label = u'Export Exposure Metadata'

    def get_tool_link(self, exposure_object):
        try:
            exposure, workspace, path = getAdapter(
                exposure_object, IExposureSourceAdapter).source()
        except Exception:
            return None
        return exposure.absolute_url() + '/virtuoso_rdf'
