# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger

PROFILE_ID = 'profile-rg.prenotazioni:default'


def update_workflow(context):
    """
    Update workflow method
    """
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'workflow')
    logger.info("Workflow has been updated")
