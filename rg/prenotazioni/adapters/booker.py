# -*- coding: utf-8 -*-
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from DateTime import DateTime
from Products.CMFPlone.FactoryTool import _createObjectByType
from plone import api
from random import choice
from rg.prenotazioni.config import MIN_IN_DAY
from zope.component import Interface
from zope.interface.declarations import implements


class IBooker(Interface):
    '''
    Interface for a booker
    '''


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def get_or_create_obj(folder, key, portal_type):
    '''
    Get the object with id key from folder
    If it does not exist create an object with the given key and portal_type

    :param folder: a Plone folderish object
    :param key: the key of the child object
    :param portal_type: the portal_type of the child object
    '''
    if key in folder:
        return folder[key]
    obj = _createObjectByType(portal_type, folder, key)
    obj.setTitle(key)
    obj.unmarkCreationFlag()
    obj.reindexObject()
    return obj


class Booker(object):
    implements(IBooker)
    portal_type = 'Prenotazione'
    day_type = 'PrenotazioniDay'
    week_type = 'PrenotazioniWeek'
    year_type = 'PrenotazioniYear'

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
        booking_date = data['booking_date']
        if isinstance(booking_date, basestring):
            booking_date = DateTime(booking_date)
        year_id = booking_date.strftime('%Y')
        year = get_or_create_obj(self.context, year_id, self.year_type)
        week_id = booking_date.strftime('%W')
        week = get_or_create_obj(year, week_id, self.week_type)
        day_id = booking_date.strftime('%u')
        day = get_or_create_obj(week, day_id, self.day_type)
        return day

    def getTipologiaDuration(self, name):
        ''' Return the duration for a given tipologia
        '''
        tipologie = self.context.getTipologia()
        for t in tipologie:
            if t['name'] == name:
                return t['duration']
        return 1

    def _create(self, data, force_gate=''):
        ''' Create a Booking object
        '''
        container = self.get_container(data)
        key = container.generateUniqueId(self.portal_type)
        obj = _createObjectByType(self.portal_type, container, key)
        # map form data to AT fields
        data_prenotazione = DateTime(data['booking_date'])
        tipology = data.get('tipology', '')
        data_scadenza = (data_prenotazione
                         + float(self.getTipologiaDuration(tipology)) / MIN_IN_DAY)
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
        fake_data = {'booking_date': booking.getData_prenotazione()}
        old_container = booking.aq_parent
        new_container = self.get_container(fake_data)
        if old_container == new_container:
            return
        booking_id = booking.getId()
        cut_data = old_container.manage_cutObjects(booking_id)
        paste_data = new_container.manage_pasteObjects(cut_data)
        [new_container[data['new_id']].reindexObject() for data in paste_data]
