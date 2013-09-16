# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger
from rg.prenotazioni.interfaces import IPrenotazione

PROJECTNAME = 'rg.prenotazioni'
PROFILE_ID = 'profile-rg.prenotazioni:default'


def upgrade(upgrade_product, version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            qi = getToolByName(context, 'portal_quickinstaller')
            p = qi.get(upgrade_product)
            setattr(p, 'installedversion', version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func


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


@upgrade(PROJECTNAME, '3000')
def run_all_steps(context):
    '''
    Run all the needed steps to upgrade to 3000
    '''
    set_expiration_date(context)

