# -*- coding: utf-8 -*-
from rg.prenotazioni.content.prenotazione import IPrenotazione  # NOQA E501
from rg.prenotazioni.testing import RG_PRENOTAZIONI_INTEGRATION_TESTING  # noqa
from plone import api
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


class PrenotazioneIntegrationTest(unittest.TestCase):

    layer = RG_PRENOTAZIONI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'PrenotazioniDay',
            self.portal,
            'prenotazione',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_prenotazione_schema(self):
        fti = queryUtility(IDexterityFTI, name='Prenotazione')
        schema = fti.lookupSchema()
        self.assertEqual(IPrenotazione, schema)

    def test_ct_prenotazione_fti(self):
        fti = queryUtility(IDexterityFTI, name='Prenotazione')
        self.assertTrue(fti)

    def test_ct_prenotazione_factory(self):
        fti = queryUtility(IDexterityFTI, name='Prenotazione')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IPrenotazione.providedBy(obj),
            u'IPrenotazione not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_prenotazione_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Prenotazione',
            id='prenotazione',
        )

        self.assertTrue(
            IPrenotazione.providedBy(obj),
            u'IPrenotazione not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_prenotazione_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Prenotazione')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
