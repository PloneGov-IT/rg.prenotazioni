# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone.FactoryTool import _createObjectByType
from random import choice
from zope.component import Interface
from zope.interface.declarations import implements


class IBooker(Interface):
    '''
    Interface for a booker
    '''


class Booker(object):
    implements(IBooker)
    portal_type = 'Prenotazione'

    def __init__(self, context):
        '''
        @param context: a PrenotazioniFolder object
        '''
        self.context = context

    def check_less_used_gates(self, data_prenotazione):
        '''
        Find which gate is les busy the day of the booking
        '''
        pcs = self.context.restrictedTraverse('@@prenotazioni_context_state')
        counter = pcs.gates_stats_in_day(data_prenotazione, only_free=True)
        if not counter:
            return ''
        min_times = min(counter.keys())
        # Get a random choice among the less busy one
        return choice(counter[min_times])

    def get_available_gate(self, data_prenotazione):
        '''
        Find which gate is free to serve this booking
        '''
        pcs = self.context.restrictedTraverse('@@prenotazioni_context_state')
        if not pcs.get_gates():
            return ''
        available_gates = pcs.get_free_gates_in_slot(data_prenotazione)
        if len(available_gates) == 1:
            return available_gates.pop()
        return self.check_less_used_gates(data_prenotazione)

    def create(self, data, force_gate=''):
        '''
        Create a Booking object
        '''
        key = self.context.generateUniqueId(self.portal_type)
        obj = _createObjectByType(self.portal_type, self.context, key)
        # map form data to AT fields
        data_prenotazione = DateTime(data['booking_date'])
        at_data = {'title': data['fullname'],
                   'description': data['subject'] or '',
                   'azienda': data['agency'] or '',
                   'data_prenotazione': data_prenotazione,
                   'telefono': data.get('phone', ''),
                   'mobile': data.get('mobile', ''),
                   'email': data['email'] or '',
                   'tipologia_prenotazione': data.get('tipology', ''),
                   }
        if not force_gate:
            at_data['gate'] = self.get_available_gate(data_prenotazione)
        else:
            at_data['gate'] = force_gate
        obj.processForm(values=at_data)
        return obj
