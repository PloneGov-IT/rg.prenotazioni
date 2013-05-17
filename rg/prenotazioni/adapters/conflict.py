# -*- coding: utf-8 -*-
from zope.component import Interface
from zope.interface.declarations import implements


class IConflictManager(Interface):
    '''
    Interface for a booker
    '''


class ConflictManager(object):
    implements(IConflictManager)
    portal_type = 'Prenotazione'

    def __init__(self, context):
        '''
        @param context: a PrenotazioniFolder object
        '''
        self.context = context

    def conflicts(self, data):
        '''
        Check if we already have a conflctual prenotation
        '''
        return False
