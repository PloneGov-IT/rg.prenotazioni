# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rg.prenotazioni.testing import RG_PRENOTAZIONI_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that rg.prenotazioni is properly installed."""

    layer = RG_PRENOTAZIONI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if rg.prenotazioni is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'rg.prenotazioni'))

    def test_browserlayer(self):
        """Test that IRgPrenotazioniLayer is registered."""
        from rg.prenotazioni.interfaces import (
            IRgPrenotazioniLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IRgPrenotazioniLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = RG_PRENOTAZIONI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['rg.prenotazioni'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if rg.prenotazioni is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'rg.prenotazioni'))

    def test_browserlayer_removed(self):
        """Test that IRgPrenotazioniLayer is removed."""
        from rg.prenotazioni.interfaces import \
            IRgPrenotazioniLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IRgPrenotazioniLayer,
            utils.registered_layers())
