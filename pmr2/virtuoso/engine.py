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

