from cStringIO import StringIO

import zope.interface
import zope.component

from pmr2.app.workspace.browser.browser import FilePage

from pmr2.rdf.base import RdfXmlObject


class RdfPage(FilePage):

    def render(self):
        super(RdfPage, self).update()

        if not self.data:
            raise NotFound(self.context, self.context.title_or_id())

        contents = self.data['contents']()
        s = StringIO(contents)
        rdf = RdfXmlObject()
        rdf.parse(s)
        contents = rdf.graph.serialize()

        if not isinstance(contents, basestring):
            # Not a normal file, we don't know what to do.
            raise NotFound(self.context, self.context.title_or_id())

        mimetype = 'text/xml'
        self.request.response.setHeader('Content-Type', mimetype)
        self.request.response.setHeader('Content-Length', len(contents))
        return contents
