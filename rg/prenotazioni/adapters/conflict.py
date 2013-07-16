# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from zope.component import Interface
from zope.interface.declarations import implements


class IConflictManager(Interface):
    '''
    Interface for a booker
    '''


class ConflictManager(object):
    implements(IConflictManager)
    portal_type = 'Prenotazione'
    # We consider only this state as active. I.e.: prenotazioni rejected are
    # not counted!
    active_review_state = ['published', 'pending']

    def __init__(self, context):
        '''
        @param context: a PrenotazioniFolder object
        '''
        self.context = context

    @property
    @memoize
    def base_query(self):
        '''
        A query that returns objects in this context
        '''
        return {'portal_type': self.portal_type,
                'path': '/'.join(self.context.getPhysicalPath())}

    def get_limit(self):
        '''
        Get's the limit for concurrent objects
        It is given by the number of active gates (if specified)
        or defaults to one
        There is also a field that disables gates, we should remove them from
        this calculation
        '''
        pcs = self.context.restrictedTraverse('@@prenotazioni_context_state')
        if not pcs.get_gates():
            return 1
        return len(pcs.get_available_gates())

    def unrestricted_prenotazioni(self, **kw):
        '''
        Query our prenotazioni
        '''
        query = self.base_query.copy()
        query.update(kw)
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc.unrestrictedSearchResults(**query)
        return brains

    def is_vacation_day(self, date):
        '''
        Check if today is a vacation day
        '''
        date_it = date.strftime('%d/%m/%Y')
        festivi = self.context.getFestivi()
        return date_it in festivi

    def has_free_slots(self, date):
        '''
        Calculate free slots
        '''
        date = DateTime(date)
        if self.is_vacation_day(date):
            return False
        query = {'Date': date,
                 'review_state': self.active_review_state}
        concurrent_prenotazioni = self.unrestricted_prenotazioni(**query)
        busy_slots = len(concurrent_prenotazioni)
        limit = self.get_limit()
        return limit - busy_slots > 0

    def conflicts(self, data):
        '''
        Check if we already have a conflictual booking
        '''
        if not data.get('booking_date'):
            return False
        return not self.has_free_slots(data['booking_date'])
