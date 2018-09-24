# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import rg.prenotazioni


class RgPrenotazioniLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=rg.prenotazioni)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'rg.prenotazioni:default')


RG_PRENOTAZIONI_FIXTURE = RgPrenotazioniLayer()


RG_PRENOTAZIONI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RG_PRENOTAZIONI_FIXTURE,),
    name='RgPrenotazioniLayer:IntegrationTesting',
)


RG_PRENOTAZIONI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RG_PRENOTAZIONI_FIXTURE,),
    name='RgPrenotazioniLayer:FunctionalTesting',
)


RG_PRENOTAZIONI_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        RG_PRENOTAZIONI_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='RgPrenotazioniLayer:AcceptanceTesting',
)
