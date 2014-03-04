import zope.interface
import zope.component
from zope.schema import fieldproperty
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation import factory
from zope.container.contained import Contained
from persistent import Persistent

from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo


@zope.component.adapter(IAttributeAnnotatable)
@zope.interface.implementer(IWorkspaceRDFInfo)
class WorkspaceRDFInfo(Persistent, Contained):

    paths = fieldproperty.FieldProperty(IWorkspaceRDFInfo['paths'])


WorkspaceRDFInfoFactory = factory(WorkspaceRDFInfo)
