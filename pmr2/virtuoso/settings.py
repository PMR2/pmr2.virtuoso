from persistent import Persistent
from requests.auth import HTTPDigestAuth
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
    graph_prefix = FieldProperty(ISettings['graph_prefix'])
    sparql_endpoint = FieldProperty(ISettings['sparql_endpoint'])

    @property
    def requests_auth(self):
        return HTTPDigestAuth(self.user, self.password)

SettingsFactory = settings_factory(
    Settings, 'pmr2_virtuoso', u'Virtuoso Settings')
