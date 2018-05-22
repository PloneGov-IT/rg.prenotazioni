# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import rg.prenotazioni


class PrenotazioniLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=rg.prenotazioni)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'rg.prenotazioni:default')


PRENOTAZIONI_FIXTURE = PrenotazioniLayer()


PRENOTAZIONI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRENOTAZIONI_FIXTURE,),
    name='PrenotazioniLayer:IntegrationTesting'
)


PRENOTAZIONI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRENOTAZIONI_FIXTURE,),
    name='PrenotazioniLayer:FunctionalTesting'
)


PRENOTAZIONI_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PRENOTAZIONI_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PrenotazioniLayer:AcceptanceTesting'
)
