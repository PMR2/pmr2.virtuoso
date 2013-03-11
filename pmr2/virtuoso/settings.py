from persistent import Persistent
import zope.interface
import zope.component
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings import settings_factory

from pmr2.virtuoso.interfaces import ISettings


class Settings(Persistent, Contained):
    zope.interface.implements(ISettings)
    zope.component.adapts(IPMR2GlobalSettings)

    user = FieldProperty(ISettings['user'])
    password = FieldProperty(ISettings['password'])
    odbc_source = FieldProperty(ISettings['odbc_source'])

    @property
    def source(self):
        return 'virtuoso://%s:%s@%s' % (
            self.user, self.password, self.odbc_source)

SettingsFactory = settings_factory(
    Settings, 'pmr2_virtuoso', u'Virtuoso Settings')