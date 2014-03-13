import zope.interface
import zope.schema


class ISettings(zope.interface.Interface):

    # required should be true, however tests for pmr2.app.settings
    # really should have better isolation from extended forms.

    user = zope.schema.TextLine(
        title=u'DB user name',
        default=u'dba',
        required=False,
    )

    # z3c.form way of handling Password is broken, as empty string is
    # considered as a valid password.
    #password = zope.schema.Password(

    password = zope.schema.TextLine(
        title=u'DB password',
        default=u'dba',
        required=False,
    )

    odbc_source = zope.schema.TextLine(
        title=u'ODBC Source',
        description=u"The definition for the Virtuoso instance to connect "
                     "to in odbc.ini.  This is located in $HOME/.odbc.ini or "
                     "/etc/odbc.ini, or consult your system's documentation.",
        default=u'VOS',
        required=False,
    )

    sparql_endpoint = zope.schema.TextLine(
        title=u'SPQRAL Endpoint',
        description=u"The SPARQL only end point.  May deprecate ODBC access.",
        default=u'http://localhost:8890/sparql',
        required=False,
    )


class IEngine(zope.interface.Interface):
    """Interface to the engine."""


class IWorkspaceRDFInfo(zope.interface.Interface):
    """
    Interface to the annotation that tracks the paths that are to be
    indexed with the RDF Store.
    """

    paths = zope.schema.List(
        title=u'RDF Paths',
        description=u'Paths that will be indexed as RDF.',
        required=False,
        value_type=zope.schema.Choice(
            vocabulary='pmr2.vocab.manifest',
        )
    )


class IWorkspaceRDFIndexer(zope.interface.Interface):
    """
    The adapter that provides the method that collects the marked RDF
    paths and indexes the content into the RDF store.
    """
