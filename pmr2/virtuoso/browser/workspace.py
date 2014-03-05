import zope.component
import zope.interface
import zope.schema
import z3c.form
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform.form import EditForm

from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo


class WorkspaceRDFInfoEditForm(EditForm):

    fields = z3c.form.field.Fields(IWorkspaceRDFInfo)

    imported = None
    omitted = None

    def getContent(self):
        return zope.component.getAdapter(self.context, IWorkspaceRDFInfo)
