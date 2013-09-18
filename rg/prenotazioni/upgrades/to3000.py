# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger
from rg.prenotazioni.interfaces import IPrenotazione
from rg.prenotazioni.adapters.booker import IBooker

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
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="PrenotazioniFolder")
    query = {'portal_type': 'Prenotazione'}
    for brain in brains:
        obj = brain.getObject()
        booker = IBooker(obj)
        bookings = obj.listFolderContents(query)
        for booking in bookings:
            booker.fix_container(booking)
            logger.info("Fix container for %s"
                        % '/'.join(booking.getPhysicalPath()))


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


def upgrade_week_values(context):
    ''' Upgrade values of settimana_tipo for prenotazioni_folder content type
    '''
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="PrenotazioniFolder")
    for brain in brains:
        obj = brain.getObject()
        span = obj.getDurata()
        week = obj.getSettimana_tipo()
        if week:
            for day in week:
                get_merge_time(day, span)
    logger.info('Updated values for prenotazioni_folder in %s' % PROFILE_ID)


def get_merge_time(day, span):
    ''' Utiliy function
    '''
    num_m = day.pop('num_m', '')
    num_p = day.pop('num_p', '')
    if num_m:
        m_time = day.get('inizio_m', '0')
        day['end_m'] = get_end_time(m_time, num_m, span)
    if num_p:
        p_time = day.get('inizio_p', '0')
        day['end_p'] = get_end_time(p_time, num_p, span)


def get_end_time(starttime, num, span):
    ''' Utility function
    '''
    if not starttime or len(starttime) < 4:
        return '0000'
    m = int(starttime[2:])
    hour = int(starttime[:2]) + (m + int(num) * span) / 60
    minute = (m + int(num) * span) % 60
    return str(hour).zfill(2) + str(minute).zfill(2)


