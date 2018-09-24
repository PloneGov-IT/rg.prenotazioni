# -*- coding: utf-8 -*-
from rg.prenotazioni.content.prenotazioni_week import IPrenotazioniWeek  # NOQA E501
from rg.prenotazioni.testing import RG_PRENOTAZIONI_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


class PrenotazioniWeekIntegrationTest(unittest.TestCase):

    layer = RG_PRENOTAZIONI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'PrenotazioniYear',
            self.portal,
            'prenotazioni_week',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_prenotazioni_week_schema(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniWeek')
        schema = fti.lookupSchema()
        self.assertEqual(IPrenotazioniWeek, schema)

    def test_ct_prenotazioni_week_fti(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniWeek')
        self.assertTrue(fti)

    def test_ct_prenotazioni_week_factory(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniWeek')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IPrenotazioniWeek.providedBy(obj),
            u'IPrenotazioniWeek not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_prenotazioni_week_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='PrenotazioniWeek',
            id='prenotazioni_week',
        )

        self.assertTrue(
            IPrenotazioniWeek.providedBy(obj),
            u'IPrenotazioniWeek not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_prenotazioni_week_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='PrenotazioniWeek')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_prenotazioni_week_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='PrenotazioniWeek')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'prenotazioni_week_id',
            title='PrenotazioniWeek container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
