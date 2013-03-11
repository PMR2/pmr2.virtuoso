import logging

import sqlalchemy
from sqlalchemy.sql import bindparam

import zope.component
import zope.interface

from Products.CMFCore.utils import getToolByName

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.util import quote_url

logger = logging.getLogger('pmr2.virtuoso.engine')


class Engine(object):
    """
    SQL Alchemy engine adapter helper class
    """

    zope.interface.implements(IEngine)

    def __init__(self, settings):
        source = settings.source
        self._engine = sqlalchemy.create_engine(source)

    def importRdf(self, url, graph='urn:example:pmr2.virtuoso'):
        conn = self._engine.connect()
        trans = conn.begin()
        sqltmpl = 'sparql load <%(source)s> into graph <%(graph)s>'
        sqlstr = sqltmpl % {
            'source': quote_url(url), 'graph': quote_url(graph)}
        try:
            lr = conn.execute(sqlstr)
            lr.close()
        except:
            logger.error('fail to execute sql', exc_info=1)
        trans.commit()

    def bulkImportRdf(self, urls, graph='urn:example:pmr2.virtuoso'):
        engine = self._engine
        for source in urls:
            self.importRdf(source, graph)

    def importExposureFilesRdf(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
            pmr2_review_state='published',
            portal_type='ExposureFile',
            # Subject='CellML Model',
        )

        for b in brains:
            bo = b.getObject()
            es = zope.component.getAdapter(bo, IExposureSourceAdapter)
            e, w, p = es.source()
            try:
                if w is None:
                    raise TypeError("%s cannot be adapted to workspace" % bo)
                source = '%s/%s/%s/%s/%s' % (
                    portal_url, w.absolute_url(), 'pmr2_rdf', e.commit_id, p)
                self.importRdf(source)
            except:
                logger.error('fail to acquire workspace file', exc_info=1)
