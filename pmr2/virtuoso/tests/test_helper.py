import unittest

from pmr2.virtuoso.helper import quote_url


class QuoteUrlTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0000_base(self):
        self.assertEqual('http://example.com/test',
            quote_url('http://example.com/test'),)

    def test_0001_already_escaped(self):
        self.assertEqual('http://example.com/test%20test',
            quote_url('http://example.com/test%20test'),)

    def test_0002_mixed(self):
        self.assertEqual('http://example.com/test%20test/test%20test%20test',
            quote_url('http://example.com/test%20test%2ftest+test test'),)

    def test_0010_target_escape(self):
        self.assertEqual(
            'http://example.com/%22%3E%3B%20drop%20table%20students%20--',
            quote_url('http://example.com/">; drop table students --'),)

    def test_0100_query_base(self):
        self.assertEqual('http://example.com/?q=test',
            quote_url('http://example.com/?q=test'),)

    def test_0102_query_mixed(self):
        self.assertEqual('http://example.com/?q=test+test%2F%2Ftest+test+test',
            quote_url('http://example.com/?q=test%20test/%2ftest+test test'),)

    def test_0101_query_already_escaped(self):
        self.assertEqual('http://example.com/?q=test+query',
            quote_url('http://example.com/?q=test+query'),)

    def test_0110_target_query_escape(self):
        self.assertEqual(
            'http://example.com/?q=1%22%3E%3B+drop+table+students+--',
            quote_url('http://example.com/?q=1">; drop table students --'),)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuoteUrlTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

