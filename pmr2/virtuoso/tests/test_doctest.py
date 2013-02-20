import unittest
import doctest

from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc

from pmr2.app.workspace.tests.base import WorkspaceDocTestCase
from pmr2.virtuoso.tests import base


def test_suite():
    return unittest.TestSuite([

        # Content tests.
        ztc.ZopeDocFileSuite(
            'README.rst', package='pmr2.virtuoso',
            test_class=WorkspaceDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
