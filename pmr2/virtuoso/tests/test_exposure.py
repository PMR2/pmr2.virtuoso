import unittest

import zope.component
import zope.interface

from Zope2.App import zcml
from Products.Five import fiveconfigure

from pmr2.app.exposure.browser.browser import ExposureFileAnnotatorForm
from pmr2.app.exposure.browser.browser import ExposureFileNoteEditForm
from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.annotation.interfaces import IExposureFileAnnotator
from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.annotator import VirtuosoAnnotator

from pmr2.virtuoso.testing.layer import \
    PMR2_VIRTUOSO_EXPOSURE_INTEGRATION_LAYER
from pmr2.testing.base import TestRequest


class ExposureTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_EXPOSURE_INTEGRATION_LAYER

    def test_exposure_rdf_annotation(self):
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)
        engine._clear()

        self.assertEqual(len(engine.stmts), 0)

        exposure = self.layer['portal'].virtuoso_exposure.virtuoso_test
        context = exposure['simple.rdf']
        request = TestRequest(form={
            'form.widgets.annotators': [u'virtuoso_rdf'],
            'form.buttons.apply': 1,
        })
        view = ExposureFileAnnotatorForm(context, request)
        view.update()

        # this should have indexed.
        self.assertEqual(len(engine.stmts), 2)

        engine._clear()
        # follow up with post annotation
        request = TestRequest(form={
            'form.widgets.exclude_nav': 1,
            'form.buttons.apply': 1,
        })
        annotator = zope.component.getUtility(IExposureFileAnnotator,
            name='virtuoso_rdf')(context, request)
        annotator(data=(('exclude_nav', 1),))

        note = zope.component.getAdapter(context, name='virtuoso_rdf')

        self.assertEqual(len(engine.stmts), 2)
        self.assertEqual(
            engine.stmts[0],
            'CLEAR GRAPH <urn:pmr:virtuoso:/plone/'
                'virtuoso_exposure/virtuoso_test/simple.rdf>'
        )

        self.assertTrue(context.getExcludeFromNav())

        annotator = zope.component.getUtility(IExposureFileAnnotator,
            name='virtuoso_rdf')(context, request)
        annotator(data=(('exclude_nav', 0),))
        self.assertFalse(context.getExcludeFromNav())

    def test_exposure_rdf_annotation_data_optional(self):
        # data is actually optionally provided sometimes due to how
        # there is only one field.
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)
        engine._clear()

        self.assertEqual(len(engine.stmts), 0)

        exposure = self.layer['portal'].virtuoso_exposure.virtuoso_test
        context = exposure['simple.rdf']
        request = TestRequest(form={
            'form.widgets.annotators': [u'virtuoso_rdf'],
            'form.buttons.apply': 1,
        })
        view = ExposureFileAnnotatorForm(context, request)
        view.update()

        engine._clear()

        # follow up with post annotation
        request = TestRequest(form={
            'form.widgets.exclude_nav': 1,
            'form.buttons.apply': 1,
        })
        annotator = zope.component.getUtility(IExposureFileAnnotator,
            name='virtuoso_rdf')(context, request)
        # again, this has provided no data.
        annotator(data=())

        note = zope.component.getAdapter(context, name='virtuoso_rdf')

        self.assertEqual(len(engine.stmts), 2)
        self.assertEqual(
            engine.stmts[0],
            'CLEAR GRAPH <urn:pmr:virtuoso:/plone/'
                'virtuoso_exposure/virtuoso_test/simple.rdf>',
        )
