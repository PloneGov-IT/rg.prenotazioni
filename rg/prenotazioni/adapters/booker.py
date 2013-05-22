# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone.FactoryTool import _createObjectByType
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

    def create(self, data):
        '''
        Create a Booking object
        '''
        key = self.context.generateUniqueId(self.portal_type)
        obj = _createObjectByType(self.portal_type, self.context, key)
        # map form data to AT fields
        at_data = {'title': data['fullname'],
                   'description': data['subject'] or '',
                   'azienda': data['agency'] or '',
                   'data_prenotazione': DateTime(data['booking_date']),
                   'telefono': data['phone'] or '',
                   'email': data['email'] or '',
                   'tipologia_prenotazione': data.get('tipology', ''),
                   }
        obj.processForm(values=at_data)
        return obj
