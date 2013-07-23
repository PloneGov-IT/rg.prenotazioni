# -*- coding: utf-8 -*-
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from datetime import timedelta
from plone.memoize.view import memoize
from rg.prenotazioni import time2timedelta
from rg.prenotazioni.adapters.conflict import IConflictManager


class PrenotazioniContextState(BrowserView):
    '''
    This is a view to for checking prenotazioni context state
    '''
    active_review_state = ['published', 'pending']

    @memoize
    def get_gates(self):
        '''
        Get's the gates, available and unavailable
        '''
        return self.context.getGates()

    @memoize
    def get_unavailable_gates(self):
        '''
        Get's the gates declared unavailable
        '''
        return self.context.getUnavailable_gates()

    @memoize
    def get_available_gates(self):
        '''
        Get's the gates declared available
        '''
        total = set(self.get_gates())
        unavailable = set(self.get_unavailable_gates())
        return total - unavailable

    def get_busy_gates_in_slot(self, booking_date):
        '''
        The gates already associated to a Prenotazione object for booking_date

        :param booking_date: a DateTime object
        '''
        adapter = IConflictManager(self.context)
        brains = adapter.unrestricted_prenotazioni(Date=booking_date)
        return set([x._unrestrictedGetObject().getGate() for x in brains])

    def get_free_gates_in_slot(self, booking_date):
        '''
        The gates not associated to a Prenotazione object for booking_date

        :param booking_date: a DateTime object
        '''
        available = set(self.get_available_gates())
        busy = set(self.get_busy_gates_in_slot(booking_date))
        return available - busy

    def search_bookings_in_day(self, booking_date):
        '''
        The Prenotazione objects for today

        :param booking_date: a DateTime object
        '''
        adapter = IConflictManager(self.context)
        query = {'query': [booking_date.strftime('%Y/%m/%d 00:00'),
                           booking_date.strftime('%Y/%m/%d 23:59')],
                 'range': 'minmax'}
        return adapter.unrestricted_prenotazioni(Date=query)

    def gates_stats_in_day(self, booking_date, only_free=False):
        '''
        Get's the stats about occupation for today

        This is a dictionary that maps the number of times a gate was busy
        today with a list of gates, e.g.:
        counter = {0: ['Gate X']
                   2: ['Gate 1', 'Gate 2']}

        :param booking_date: a DateTime object
        '''
        booked_gates = [x._unrestrictedGetObject().getGate()
                        for x in self.search_bookings_in_day(booking_date)]
        stats = {}
        if only_free:
            gates = self.get_free_gates_in_slot(booking_date)
        else:
            gates = self.get_gates()
        for gate in gates:
            stats.setdefault(booked_gates.count(gate), []).append(gate)
        return stats

    def get_slots_by_weekday(self, weekday):
        '''
        Find the slots by weekday

        Weekday, according to datetime.date is:
         0. monday
         1. tuesday
         ...
         6. sunday

        We are returning slots as datetime.timedelta objects
        E.g.:
        {'m': [datetime.datetime(2013, 7, 16, 7, 15),
               datetime.datetime(2013, 7, 16, 7, 40),
               ...],
         'p': [],
        }
        '''
        slots = {'m': [],
                 'p': [],
        }
        day = self.context.getSettimana_tipo()[weekday]
        slot_time = int(self.context.getDurata())
        slot_time = timedelta(minutes=slot_time)

        for marker in ('m', 'p'):
            key = 'inizio_%s' % marker
            start = day[key]
            if start != '0':
                start = time2timedelta(start)
                key = 'num_%s' % marker
                slots[marker] = [(start + i * slot_time)
                                 for i in range(int(day[key]))]
        return slots

    def get_slots_in_day(self, booking_date):
        '''
        Find the slots in booking_date

        Slots are divided in morning/afternoon slots.
        {'m': ['09:00', '09:30', ...]
         'p': ['14:00', '14:30', ...]
        }
        '''
        booking_date = booking_date.asdatetime()
        slots = self.get_slots_by_weekday(booking_date.weekday())
        for marker in slots:
            slots[marker] = [booking_date + time for time in slots[marker]]
        return slots
