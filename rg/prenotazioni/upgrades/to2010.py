# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniLogger as logger


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
    Install quintagroup.formlib.captcha
    '''
    missing_products = ['quintagroup.captcha.core']
    qi = getToolByName(context, 'portal_quickinstaller')
    for product in missing_products:
        if not qi.isProductInstalled(product):
            logger.info('Installing %s' % product)
            qi.installProduct(product)
