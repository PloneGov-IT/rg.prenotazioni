# -*- coding: utf-8 -*-
from rg.prenotazioni.content.prenotazioni_year import IPrenotazioniYear  # NOQA E501
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


class PrenotazioniYearIntegrationTest(unittest.TestCase):

    layer = RG_PRENOTAZIONI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'PrenotazioniFolder',
            self.portal,
            'prenotazioni_year',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_prenotazioni_year_schema(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniYear')
        schema = fti.lookupSchema()
        self.assertEqual(IPrenotazioniYear, schema)

    def test_ct_prenotazioni_year_fti(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniYear')
        self.assertTrue(fti)

    def test_ct_prenotazioni_year_factory(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniYear')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IPrenotazioniYear.providedBy(obj),
            u'IPrenotazioniYear not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_prenotazioni_year_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='PrenotazioniYear',
            id='prenotazioni_year',
        )

        self.assertTrue(
            IPrenotazioniYear.providedBy(obj),
            u'IPrenotazioniYear not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_prenotazioni_year_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='PrenotazioniYear')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_prenotazioni_year_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='PrenotazioniYear')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'prenotazioni_year_id',
            title='PrenotazioniYear container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
