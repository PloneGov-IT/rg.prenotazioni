# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone.FactoryTool import _createObjectByType
from plone import api
from plone.memoize.instance import memoize
from random import choice
from rg.prenotazioni.config import MIN_IN_DAY
from zope.component import Interface
from zope.interface.declarations import implements


class IBooker(Interface):
    ''' Interface for a booker
    '''


class Booker(object):
    implements(IBooker)
    portal_type = 'Prenotazione'

    def __init__(self, context):
        '''
        @param context: a PrenotazioniFolder object
        '''
        self.context = context

    @property
    @memoize
    def prenotazioni(self):
        ''' The prenotazioni context state view
        '''
        return self.context.restrictedTraverse('@@prenotazioni_context_state')

    def get_available_gate(self, data_prenotazione):
        '''
        Find which gate is free to serve this booking
        '''
        if not self.prenotazioni.get_gates():
            return ''
        available_gates = (self.prenotazioni
                           .get_free_gates_in_slot(data_prenotazione))
        if len(available_gates) == 1:
            return available_gates.pop()
        return choice(self.prenotazioni.get_less_used_gates())

    def _create(self, data, force_gate=''):
        ''' Create a Booking object
        '''
        booking_date = data['booking_date']
        container = self.prenotazioni.get_container(booking_date)
        key = container.generateUniqueId(self.portal_type)
        obj = _createObjectByType(self.portal_type, container, key)
        # map form data to AT fields
        data_prenotazione = DateTime(booking_date)
        tipology = data.get('tipology', '')
        data_scadenza = (data_prenotazione
                         + float(self.prenotazioni
                                 .get_tipology_duration(tipology)) / MIN_IN_DAY)
        at_data = {'title': data['fullname'],
                   'description': data['subject'] or '',
                   'azienda': data['agency'] or '',
                   'data_prenotazione': data_prenotazione,
                   'data_scadenza': data_scadenza,
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

    def create(self, data, force_gate=''):
        '''
        Create a Booking object

        Like create but we disable security checks to allow creation
        for anonymous users
        '''
        with api.env.adopt_roles(['Manager', 'Member']):
            return self._create(data, force_gate)

    def fix_container(self, booking):
        ''' Take a booking and move it to the right week
        '''
        booking_date = booking.getData_prenotazione().asdatetime()
        old_container = booking.aq_parent
        new_container = self.prenotazioni.get_container(booking_date)
        if old_container == new_container:
            return
        api.content.move(booking, new_container)
