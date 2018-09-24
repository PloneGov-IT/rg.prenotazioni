# -*- coding: utf-8 -*-
from rg.prenotazioni.content.prenotazioni_folder import IPrenotazioniFolder  # NOQA E501
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


class PrenotazioniFolderIntegrationTest(unittest.TestCase):

    layer = RG_PRENOTAZIONI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_prenotazioni_folder_schema(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniFolder')
        schema = fti.lookupSchema()
        self.assertEqual(IPrenotazioniFolder, schema)

    def test_ct_prenotazioni_folder_fti(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniFolder')
        self.assertTrue(fti)

    def test_ct_prenotazioni_folder_factory(self):
        fti = queryUtility(IDexterityFTI, name='PrenotazioniFolder')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IPrenotazioniFolder.providedBy(obj),
            u'IPrenotazioniFolder not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_prenotazioni_folder_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='PrenotazioniFolder',
            id='prenotazioni_folder',
        )

        self.assertTrue(
            IPrenotazioniFolder.providedBy(obj),
            u'IPrenotazioniFolder not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_prenotazioni_folder_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='PrenotazioniFolder')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_prenotazioni_folder_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='PrenotazioniFolder')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'prenotazioni_folder_id',
            title='PrenotazioniFolder container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
