# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone.FactoryTool import _createObjectByType
from random import choice
from rg.prenotazioni.adapters.conflict import IConflictManager
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

    def check_less_used_gates(self, gates, data_prenotazione):
        '''
        Find which gate is les busy the day of the booking
        '''
        adapter = IConflictManager(self.context)
        query = {'query': [data_prenotazione.strftime('%Y/%m/%d 00:00'),
                           data_prenotazione.strftime('%Y/%m/%d 23:59')],
                 'range': 'minmax'}
        brains = adapter.unrestricted_prenotazioni(Date=query)
        booked_gates = [x._unrestrictedGetObject().getGate() for x in brains]

        # This is a dictionary that maps the number of times a gate was busy
        # today with a list of gates, e.g.:
        # counter = {2: ['Gate 1', 'Gate 2']}
        counter = {}
        for gate in gates:
            counter.setdefault(booked_gates.count(gate), []).append(gate)
        min_times = min(counter.keys())
        # Get a random choice among the less busy one
        return choice(counter[min_times])

    def get_available_gate(self, data_prenotazione):
        '''
        Find which gate is free to serve this booking
        '''
        gates = self.context.getGates()
        if not gates:
            return ''
        else:
            gates = set(gates)
        adapter = IConflictManager(self.context)
        concurrent = adapter.unrestricted_prenotazioni(Date=data_prenotazione)
        busy_gates = set([x._unrestrictedGetObject().getGate()
                          for x in concurrent])

        available_gates = gates - busy_gates
        if len(available_gates) == 1:
            return available_gates[0]

        return self.check_less_used_gates(available_gates, data_prenotazione)

    def create(self, data):
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
                   'gate': self.get_available_gate(data_prenotazione),
                   }
        obj.processForm(values=at_data)
        return obj
