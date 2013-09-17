# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone.FactoryTool import _createObjectByType
from random import choice
from zope.component import Interface
from zope.interface.declarations import implements
from rg.prenotazioni import prenotazioniLogger


class IBooker(Interface):
    '''
    Interface for a booker
    '''


class Booker(object):
    implements(IBooker)
    portal_type = 'Prenotazione'
    container_type = 'PrenotazioniWeek'

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

    def get_container(self, data):
        ''' Get a container to store the data
        '''
        data_prenotazione = DateTime(data['booking_date'])
        key = data_prenotazione.strftime('%Y-%W')
        if not key in self.context:
            _createObjectByType(self.container_type, self.context, key)
        return self.context[key]

    def create(self, data, force_gate=''):
        '''
        Create a Booking object
        '''
        container = self.get_container(data)
        key = container.generateUniqueId(self.portal_type)
        obj = _createObjectByType(self.portal_type, container, key)
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

    def fix_container(self, booking):
        ''' Take a booking and move it to the right week
        '''
        fake_data = {'booking_date': booking.getData_prenotazione()}
        old_container = booking.aq_parent
        new_container = self.get_container(fake_data)
        if old_container == new_container:
            return
        booking_id = booking.getId()
        cut_data = old_container.manage_cutObjects(booking_id)
        new_container.manage_pasteObjects(cut_data)
