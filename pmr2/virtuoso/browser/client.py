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

    statement = zope.schema.Text(
        title=u'SPARQL Select Statement',
        description=u'The SPARQL statement to pass into query.',
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

        statement = data['statement']

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        portal = self.context  # XXX assumption based on current zcml
        client = zope.component.getMultiAdapter((portal, settings),
            ISparqlClient)

        results = client.restricted_select(statement)

        self.results = results
