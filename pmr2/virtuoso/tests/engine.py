import zope.component
import zope.interface

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.interfaces import ISettings


@zope.interface.implementer(IEngine)
class MockEngine(object):
    """
    A mock sparql engine.
    """

    zope.interface.implements(IEngine)

    def __init__(self):
        self._clear()

    def execute(self, stmt):
        self.stmts.append(stmt)

    def _clear(self):
        self.stmts = []


def Engine():
    engine = MockEngine()

    @zope.interface.implementer(IEngine)
    @zope.component.adapter(ISettings)
    def make_engine(settings):
        return engine

    return make_engine
