import json

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

    query = zope.schema.Text(
        title=u'SPARQL Select Statement',
        description=u'The SPARQL statement to pass into query.',
    )


class SparqlClientForm(PostForm):

    fields = z3c.form.field.Fields(ISparqlClientForm)
    template = ViewPageTemplateFile('sparql_client_form.pt')
    ignoreContext = True

    results = None

    def update(self):
        super(SparqlClientForm, self).update()

    @z3c.form.button.buttonAndHandler(u'Execute', name='execute')
    def handleExecute(self, action):
        """
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        query = data['query']

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        portal = self.context  # XXX assumption based on current zcml
        client = zope.component.getMultiAdapter((portal, settings),
            ISparqlClient)

        results = client.restricted_select(query)

        self.results = results


class JsonSparqlClientForm(SparqlClientForm):

    def authenticate(self):
        return True

    def extractQuery(self):
        query = self.request.form.get('query')
        if query:
            return query

        stdin = getattr(self.request, 'stdin', None)
        if stdin:
            stdin.seek(0)
            query = stdin.read()

        return query

    def update(self):
        query = self.extractQuery()
        if query:
            self.request.form['form.widgets.query'] = query
            self.request.form['form.buttons.execute'] = 'Execute'
        super(JsonSparqlClientForm, self).update()

    def render(self):
        if not self.results:
            return ''

        # non-standard
        self.results['head'].pop('graph_var')
        filtered = self.results['results'].pop('filtered_bindings')
        self.results['results']['bindings'] = list(filtered(standard=True))
        return json.dumps(self.results)
