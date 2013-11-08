# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from datetime import timedelta
from plone.memoize.instance import memoize
from rg.prenotazioni.adapters.slot import BaseSlot
from zope.component import Interface
from zope.interface.declarations import implements


class IConflictManager(Interface):

    '''
    Interface for a booker
    '''


class ConflictManager(object):
    implements(IConflictManager)
    portal_type = 'Prenotazione'
    # We consider only those state as active. I.e.: prenotazioni rejected are
    # not counted!
    active_review_state = ['published', 'pending']

    def __init__(self, context):
        '''
        @param context: a PrenotazioniFolder object
        '''
        self.context = context

    def is_vacation_day(self, date):
        '''
        Check if today is a vacation day
        '''
        date_it = date.strftime('%d/%m/%Y')
        festivi = self.context.getFestivi()
        return date_it in festivi

    @property
    @memoize
    def prenotazioni(self):
        ''' The prenotazioni context state view
        '''
        return self.context.restrictedTraverse('@@prenotazioni_context_state')

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
        if not self.prenotazioni.get_gates():
            return 1
        return len(self.prenotazioni.get_available_gates())

    def unrestricted_prenotazioni(self, **kw):
        '''
        Query our prenotazioni
        '''
        query = self.base_query.copy()
        query.update(kw)
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc.unrestrictedSearchResults(**query)
        return brains

    def search_bookings_by_date_range(self, start, stop, **kw):
        '''
        Query our prenotazioni
        '''
        query = kw.copy()
        query['Date'] = {'query': [start, stop],
                         'range': 'min:max'}
        return self.unrestricted_prenotazioni(**query)

    def get_choosen_slot(self, data):
        ''' Get's the slot requested by the user
        '''
        tipology = data.get('tipology', '')
        tipology_duration = self.prenotazioni.get_tipology_duration(tipology)
        start = data.get('booking_date', '')
        end = start + timedelta(seconds=tipology_duration * 60)
        slot = BaseSlot(start, end)
        return slot

    def conflicts(self, data):
        '''
        Check if we already have a conflictual booking
        '''
        booking_date = data.get('booking_date', '')
        slot = self.get_choosen_slot(data)
        availability = (self.prenotazioni
                        .get_free_slots(booking_date))
        for gate_slots in availability.itervalues():
            for gate_slot in gate_slots:
                if slot in gate_slot:
                    return False
        return True
