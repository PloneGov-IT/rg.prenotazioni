# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.adapters.conflict import IConflictManager
from rg.prenotazioni.config import MIN_IN_DAY
from zope.annotation.interfaces import IAnnotations

PROJECTNAME = 'rg.prenotazioni'
PROFILE_ID = 'profile-rg.prenotazioni:default'
VERSION = '3000'
ANNOTATION_ROOT = 'Archetypes.storage.AnnotationStorage-'


def get_end_time(starttime, num, span):
    ''' Utility function
    '''
    if not starttime or len(starttime) < 4:
        return ''
    m = int(starttime[2:])
    hour = int(starttime[:2]) + (m + int(num) * span) / 60
    minute = (m + int(num) * span) % 60
    return str(hour).zfill(2) + str(minute).zfill(2)


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


def getAnnotaionValue(context, field_name, fallback=()):
    ''' Utility function to get annotations value from ZODB
    '''
    key = ANNOTATION_ROOT + field_name
    annotations = IAnnotations(context)
    return annotations.get(key, fallback)


def set_expiration_date(context):
    ''' Upgrade all IPrenotazione object in order to provide the expiration
    date for each reservation
    '''

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="PrenotazioniFolder")
    for brain in brains:
        obj = brain.getObject()
        durata = getAnnotaionValue(obj, 'durata')
        if durata:
            durata = float(getAnnotaionValue(obj, 'durata')) / MIN_IN_DAY
            conflict_manager = IConflictManager(obj)
            prenotazioni = conflict_manager.unrestricted_prenotazioni()

            for prenotazione in prenotazioni:
                p = prenotazione.getObject()
                p.setData_scadenza(p.getData_prenotazione() + durata)
    logger.info("All IPrenotazione documents have been updated")


def fix_container(context):
    ''' Fix the container for Prenotazione object
    '''
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="PrenotazioniFolder")
    for brain in brains:
        obj = brain.getObject()
        booker = IBooker(obj)
        conflict_manager = IConflictManager(obj)
        bookings = conflict_manager.unrestricted_prenotazioni()
        for booking in bookings:
            booker.fix_container(booking.getObject())
        logger.info("Fixed %s objects for %s" %
                    (len(bookings), '/'.join(obj.getPhysicalPath()))
                    )


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


def upgrade_tipologia(context):
    ''' From now on "durata" and "tipologia" are merged in one single field
    This is the upgrade step which perform the merge action on
    prenotazioni_folder objects
    '''
    def new_style_tipologie(value, duration):
        ''' Check is this value should be migrated
        '''
        if isinstance(value, basestring):
            value = {'name': value, 'duration': str(duration)}
        return value

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="PrenotazioniFolder")
    for brain in brains:
        obj = brain.getObject()
        duration = getAnnotaionValue(obj, 'durata')
        items = [new_style_tipologie(item, duration)
                 for item
                 in getAnnotaionValue(obj, 'tipologia', [''])]
        obj.setTipologia(items)
    logger.info('Updated "tipologia" in prenotazioni_folder '
                ' for %s' % PROFILE_ID)


def upgrade_week_values(context):
    ''' Upgrade values of "settimana_tipo" in prenotazioni_folder content type
    '''
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="PrenotazioniFolder")
    for brain in brains:
        obj = brain.getObject()
        span = getAnnotaionValue(obj, 'durata')
        week = obj.getSettimana_tipo()
        if week:
            for day in week:
                get_merge_time(day, span)
    logger.info('Updated "settimana_tipo" in prenotazioni_folder '
                'for %s' % PROFILE_ID)
