from cStringIO import StringIO
import unittest

from pmr2.virtuoso import engine


class Engine(engine.Engine):

    def __init__(self, settings):
        # don't actually instantiate anything.
        self._engine = DummySQLEngine(self)
        self.statements = []


class DummySQLEngine(object):

    def __init__(self, parent):
        self.parent = parent

    def connect(self):
        return self

    def begin(self):
        return self

    def commit(self):
        pass

    def fetchall(self):
        return []

    def execute(self, stmt):
        self.parent.statements.append(stmt)
        return self


class BaseEngineTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0000_base(self):
        engine = Engine(None)
        engine.importRdf('http://example.com/test.rdf')
        self.assertEqual(engine.statements[0],
            'sparql load <http://example.com/test.rdf> into graph '
            '<urn:example:pmr2.virtuoso>')

    def test_0000_base(self):
        engine = Engine(None)
        engine.importRdf('http://example.com/test.rdf',
            'http://graph.example.com/')
        self.assertEqual(engine.statements[0],
            'sparql load <http://example.com/test.rdf> into graph '
            '<http://graph.example.com/>')

    def test_0010_multile_hostile(self):
        engine = Engine(None)
        engine.bulkImportRdf([
            'http://example.com/test.rdf',
            'http://example.com/test.rdf?parma=12?pwn"> into graph ',
        ], graph='urn:example:pmr2.virtuoso')
        self.assertEqual(engine.statements, [
            'sparql load <http://example.com/test.rdf> into graph '
            '<urn:example:pmr2.virtuoso>',
            'sparql load <http://example.com/test.rdf%3Fparma%3D12?'
            'pwn%22%3E+into+graph+> into graph <urn:example:pmr2.virtuoso>',
        ])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseEngineTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

