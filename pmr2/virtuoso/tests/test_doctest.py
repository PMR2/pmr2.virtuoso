import unittest
import doctest

from zope.component import testing
from Testing import ZopeTestCase as ztc

from plone.testing import layered

from pmr2.virtuoso.testing import layer


def test_suite():
    return unittest.TestSuite([

        # Content tests.
        layered(ztc.ZopeDocFileSuite(
            'README.rst', package='pmr2.virtuoso',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ), layer=layer.PMR2_VIRTUOSO_INTEGRATION_LAYER)

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
