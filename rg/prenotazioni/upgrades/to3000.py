# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger
from rg.prenotazioni.interfaces import IPrenotazione

PROJECTNAME = 'rg.prenotazioni'
PROFILE_ID = 'profile-rg.prenotazioni:default'
VERSION = '3000'


def set_expiration_date(context):
    ''' Upgrade all IPrenotazione object in order to provide the expiration
    date for each reservation
    '''
    catalog = getToolByName(context, 'portal_catalog')
    prenotazioni = catalog(object_provides=IPrenotazione.__identifier__)
    for prenotazione in prenotazioni:
        obj = prenotazione.getObject()
        scadenza = obj.getExpirationDate()
        obj.setData_scadenza(scadenza)
        logger.info("Prenotazione %s , scadenza %s" %
                    (obj.Date(), scadenza))
    logger.info("All IPrenotazione documents have been updated")


def fix_container(context):
    ''' Fix the container for Prenotazione object
    '''


def upgrade_types(context):
    ''' Upgrade portal_types to read the new PrenotazioniWeek type
    '''
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    logger.info('types.xml updated for %s' % PROFILE_ID)


def upgrade_version(context):
    '''
    Just set the version for this step
    '''
    qi = getToolByName(context, 'portal_quickinstaller')
    p = qi.get(PROJECTNAME)
    setattr(p, 'installedversion', VERSION)
