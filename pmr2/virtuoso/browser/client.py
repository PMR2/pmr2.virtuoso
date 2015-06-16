import zope.component
import zope.interface
import zope.schema

import z3c.form
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform.form import PostForm
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.virtuoso.interfaces import ISparqlClient


class ISparqlClientForm(zope.interface.Interface):

    query_variable = zope.schema.TextLine(
        title=u'Query Variables',
        description=u'List out the query variables to be returned for the '
            'query.',
    )

    triple_pattern = zope.schema.Text(
        title=u'Triple pattern',
        description=u'The triple pattern section of the query',
    )


class SparqlClientForm(PostForm):

    fields = z3c.form.field.Fields(ISparqlClientForm)
    template = ViewPageTemplateFile('sparql_client_form.pt')
    ignoreContext = True

    results = None

    @z3c.form.button.buttonAndHandler(u'Execute', name='execute')
    def handleExecute(self, action):
        """
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        portal = self.context  # XXX assumption based on current zcml
        client = zope.component.getMultiAdapter((portal, settings),
            ISparqlClient)

        results = client.restricted_select(**data)

        self.results = results
