# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger

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


@upgrade('rg.prenotazioni', '2010')
def install_missing_products(context):
    '''
    Install quintagroup.formlib.captcha and perform a workflow update
    '''
    missing_products = ['quintagroup.captcha.core']
    qi = getToolByName(context, 'portal_quickinstaller')
    for product in missing_products:
        if not qi.isProductInstalled(product):
            logger.info('Installing %s' % product)
            qi.installProduct(product)
    # Workflow update
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'workflow')
    logger.info("Workflow has been updated")


def update_actions(context):
    '''
    Run generic setup actions.xml
    '''
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'actions')
    logger.info("actions.xml has been run")
