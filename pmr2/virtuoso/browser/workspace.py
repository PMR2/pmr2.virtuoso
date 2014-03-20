import zope.component
import zope.interface
import zope.schema
import z3c.form
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform.form import EditForm

from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso.interfaces import IWorkspaceRDFIndexer

from pmr2.virtuoso.tests.engine import Engine


class WorkspaceRDFInfoEditForm(EditForm):
    z3c.form.form.extends(EditForm)

    fields = z3c.form.field.Fields(IWorkspaceRDFInfo)

    imported = None
    omitted = None

    def getContent(self):
        result = zope.component.getAdapter(self.context, IWorkspaceRDFInfo)
        parent = result.__getattribute__('__parent__')
        if len(parent.getPhysicalPath()) == 1:
            result.__setattr__('__parent__', result.__parent__)
        return result

    @z3c.form.button.buttonAndHandler(u'Apply Changes and Export To RDF Store',
                                      name='export_rdf')
    def handleExportRdf(self, action):
        """
        Export RDF selected into the RDF store.
        """

        # also update the values.
        self.handleApply(self, action)
        zope.component.getAdapter(self.context, IWorkspaceRDFIndexer)()
