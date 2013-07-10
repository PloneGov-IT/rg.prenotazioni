# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
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
