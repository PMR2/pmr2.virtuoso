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

    graph_prefix = zope.schema.TextLine(
        title=u'RDF Graph Prefix',
        description=u"The specific urn prefix for this PMR instance applied "
                     "to all exported RDF graphs.  This will uniquely "
                     "identify the triples in Virtuoso as ones belong to this "
                     "PMR instance.  WARNING: changing this will NOT affect "
                     "existing triples that were already exported, and they "
                     "will become orphaned.",
        default=u'urn:pmr:virtuoso:',
        required=False,
    )

    sparql_endpoint = zope.schema.TextLine(
        title=u'SPQRAL Endpoint',
        description=u"The SPARQL only end point.",
        default=u'http://localhost:8890/sparql',
        required=False,
    )


class IEngine(zope.interface.Interface):
    """Interface to the engine."""


class ISparqlJsonLayer(zope.interface.Interface):
    """
    Marker interface for the application/sparql-results+json mime type.
    """


class ISparqlClient(zope.interface.Interface):
    """Interface to the SPARQL only client."""

    def query(sparql_query):
        """
        The query
        """


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
    paths and indexes the content into the RDF store for a workspace.
    """


class IExposureFileAnnotatorRDFIndexer(zope.interface.Interface):
    """
    The adapter that provides the method that collects the marked RDF
    paths and indexes the content into the RDF store for the Virtuoso
    RDF annotator.
    """


# Exposure related notes.

class IVirtuosoNote(zope.interface.Interface):

    # XXX subject to change.  should be a list of triples that got indexed.
    metadata = zope.schema.Text(
        title=u'Metadata Indexed',
        description=u'The metadata (triples) added to the Virtuoso RDF store.',
        required=False,
    )

    exclude_nav = zope.schema.Bool(
        title=u'Exclude from Navigation',
        description=u'If selected, this item will not appear in the '
            'navigation tree',
        required=False,
    )


class IQueryTemplate(zope.interface.Interface):
    """
    A query template.  Actually a placeholder for now.
    """

    tokens = zope.schema.TextLine(
        title=u'Tokens',
        description=u'List of tokens to be returned',
    )

    parameters = zope.schema.List(
        title=u'Placeholders',
        description=u'A list of variable parameters to query',
    )

    template = zope.schema.Text(
        title=u'Template',
        description=u'The template',
    )


class IQueryTemplateManager(zope.interface.Interface):
    """
    Query template manager
    """

    queries = zope.schema.Dict(
        title=u'Queries',
        description=u'All saved queries',
        required=False,
        key_type=zope.schema.TextLine(title=u'Query Key'),
        value_type=zope.schema.Text(title=u'Template'),
    )
