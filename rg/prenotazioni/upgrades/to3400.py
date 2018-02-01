# -*- coding: utf-8 -*-
from plone import api
from rg.prenotazioni import prenotazioniLogger as logger
from transaction import commit

PROJECTNAME = 'rg.prenotazioni'
VERSION = '3400'


def reindex_date(context):
    ''' The Date has to be reindexed
    '''
    pc = api.portal.get_tool('portal_catalog')
    brains = pc(portal_type="Prenotazione")
    total = len(brains)
    logger.info('Found %s objects to upgrade' % len(brains))
    done = 0
    for brain in brains:
        obj = brain.getObject()
        obj.reindexObject(idxs=['Date'])
        done += 1
        if done % 100 == 0:
            commit()
            logger.info('Progress %s/%s' % (done, total))
    logger.info('Progress %s/%s' % (done, total))
