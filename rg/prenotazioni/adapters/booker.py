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
        return self.context.unrestrictedTraverse('@@prenotazioni_context_state')  # noqa

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
        return choice(self.prenotazioni
                      .get_less_used_gates(data_prenotazione.asdatetime()))

    def _create(self, data, duration=-1, force_gate=''):
        ''' Create a Booking object

        :param duration: used to force a duration. If it is negative it will be
                         calculated using the tipology
        :param force_gate: by default gates are assigned randomly except if you
                           pass this parameter.
        '''
        booking_date = data['booking_date']
        container = self.prenotazioni.get_container(booking_date,
                                                    create_missing=True)
        key = container.generateUniqueId(self.portal_type)
        obj = _createObjectByType(self.portal_type, container, key)
        # map form data to AT fields
        data_prenotazione = DateTime(booking_date)
        tipology = data.get('tipology', '')
        if duration < 0:
            # if we pass a negative duration it will be recalculated
            duration = self.prenotazioni.get_tipology_duration(tipology)
            duration = (float(duration) / MIN_IN_DAY)
        data_scadenza = (data_prenotazione + duration)
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
        api.content.transition(obj, 'submit')
        return obj

    def create(self, data, duration=-1, force_gate=''):
        '''
        Create a Booking object

        Like create but we disable security checks to allow creation
        for anonymous users
        '''
        with api.env.adopt_roles(['Manager', 'Member']):
            return self._create(data, duration=duration, force_gate=force_gate)

    def fix_container(self, booking):
        ''' Take a booking and move it to the right date
        '''
        booking_date = booking.getData_prenotazione().asdatetime()
        old_container = booking.aq_parent
        new_container = self.prenotazioni.get_container(booking_date,
                                                        create_missing=True)
        if old_container == new_container:
            return
        api.content.move(booking, new_container)
