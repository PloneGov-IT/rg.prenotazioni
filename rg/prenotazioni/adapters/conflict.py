# -*- coding: utf-8 -*-
from DateTime import DateTime
from zope.component import Interface
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName


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

    def get_limit(self):
        '''
        Get's the limit for concurrent objects
        It is given by the number of gates (if specified)
        or defaults to one
        '''
        gates = self.context.getGates()
        if not gates:
            return 1
        else:
            return len(gates)

    def has_free_slots(self, data):
        '''
        Calculate free slots
        '''
        date = DateTime(data['booking_date'])
        query = {'portal_type': self.portal_type,
                 'Date': date,
                 'path': '/'.join(self.context.getPhysicalPath())}
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc.unrestrictedSearchResults(query)
        busy_slots = len(brains)
        limit = self.get_limit()
        return limit - busy_slots > 0

    def conflicts(self, data):
        '''
        Check if we already have a conflictual booking
        '''
        return not self.has_free_slots(data)
