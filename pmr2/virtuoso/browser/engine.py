import zope.component
import zope.interface
import zope.schema

import z3c.form
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform.form import PostForm
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.virtuoso.interfaces import IEngine


class IRdfImportForm(zope.interface.Interface):

    sources = zope.schema.ASCII(
        title=u'Sources',
        description=u'List of URIs of RDF documents to import',
    )


class RdfImportForm(PostForm):

    fields = z3c.form.field.Fields(IRdfImportForm)
    template = ViewPageTemplateFile('rdf_import_form.pt')
    ignoreContext = True

    imported = None
    omitted = None

    @z3c.form.button.buttonAndHandler(u'Import RDF', name='import_rdf')
    def handleImportRdf(self, action):
        """
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)
        src = data['sources']

        portal_url = getToolByName(self.context, 'portal_url')()
        urls = [u for u in src.splitlines() if u.startswith(portal_url)]
        bads = [u for u in src.splitlines() if not u.startswith(portal_url)]

        results = engine.bulkImportRdf(urls)

        self.omitted = '\n'.join(bads)
        self.imported = '\n'.join(results)
