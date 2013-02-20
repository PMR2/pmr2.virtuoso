import zope.interface
import zope.schema


class ISettings(zope.interface.Interface):

    user = zope.schema.TextLine(
        title=u'DB user name',
        default=u'dba',
    )

    # z3c.form way of handling Password is broken, as empty string is
    # considered as a valid password.
    #password = zope.schema.Password(

    password = zope.schema.TextLine(
        title=u'DB password',
        default=u'dba',
    )

    odbc_source = zope.schema.TextLine(
        title=u'ODBC Source',
        description=u"The definition for the Virtuoso instance to connect "
                     "to in odbc.ini.  This is located in $HOME/.odbc.ini or "
                     "/etc/odbc.ini, or consult your system's documentation.",
        default=u'VOS',
    )
