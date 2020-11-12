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
    graph_prefix = FieldProperty(ISettings['graph_prefix'])
    sparql_endpoint = FieldProperty(ISettings['sparql_endpoint'])

    @property
    def source(self):
        # for standard sqlalchemy access
        return 'virtuoso://%s:%s@%s' % (
            self.user, self.password, self.odbc_source)

    @property
    def raw_source(self):
        # for raw odbc access; used by rdflib virtuoso plugin
        return "DSN=%s;UID=%s;PWD=%s;WideAsUTF16=Y;Charset=UTF-8" % (
            self.odbc_source, self.user, self.password)

SettingsFactory = settings_factory(
    Settings, 'pmr2_virtuoso', u'Virtuoso Settings')
