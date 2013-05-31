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
        return choice(list(available_gates))

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
