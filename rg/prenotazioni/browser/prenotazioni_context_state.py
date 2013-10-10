# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser import BrowserView
from datetime import date, datetime
from plone.memoize.view import memoize
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.adapters.conflict import IConflictManager
from rg.prenotazioni.adapters.slot import ISlot, BaseSlot


def hm2handm(hm):
    ''' This is a utility function that will return the hour and date of day
    to the value passed in the string hm

    :param day: a datetime date
    :param hm: a string in the format "%H%m"
    '''
    if (not hm) or (not isinstance(hm, basestring)) or (len(hm) != 4):
        raise ValueError(hm)
    return (hm[:2], hm[2:])


def hm2DT(day, hm):
    ''' This is a utility function that will return the hour and date of day
    to the value passed in the string hm

    :param day: a datetime date
    :param hm: a string in the format "%H%m"
    '''
    if not hm:
        return None
    date = day.strftime('%Y/%m/%d')
    h, m = hm2handm(hm)
    tzone = DateTime().timezone()
    return DateTime('%s %s:%s %s' % (date, h, m, tzone))


def hm2seconds(hm):
    ''' This is a utility function that will return
    to the value passed in the string hm

    :param day: a datetime date
    :param hm: a string in the format "%H%m"
    '''
    if not hm:
        return None
    h, m = hm2handm(hm)
    return int(h) * 3600 + int(m) * 60


class PrenotazioniContextState(BrowserView):

    '''
    This is a view to for checking prenotazioni context state
    '''
    active_review_state = ['published', 'pending']

    @property
    @memoize
    def today(self):
        ''' Cache for today date
        '''
        return date.today()

    @property
    @memoize
    def booker(self):
        '''
        Return the conflict manager for this context
        '''
        return IBooker(self.context)

    @property
    @memoize
    def conflict_manager(self):
        '''
        Return the conflict manager for this context
        '''
        return IConflictManager(self.context)

    @property
    @memoize
    def uid_move_booking(self):
        '''
        Get's the gates, available and unavailable
        '''
        uid = self.request.SESSION.get('UID', False)
        if not uid:
            return False
        return self.conflict_manager.unrestricted_prenotazioni(UID=uid)

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
        brains = self.conflict_manager.unrestricted_prenotazioni(
            Date=booking_date)
        return set([x._unrestrictedGetObject().getGate() for x in brains])

    def get_free_gates_in_slot(self, booking_date):
        '''
        The gates not associated to a Prenotazione object for booking_date

        :param booking_date: a DateTime object
        '''
        available = set(self.get_available_gates())
        busy = set(self.get_busy_gates_in_slot(booking_date))
        return available - busy

    @memoize
    def get_day_intervals(self, day):
        ''' Return the time ranges of this day
        '''
        weekday = day.weekday()
        week_table = self.context.getSettimana_tipo()
        day_table = week_table[weekday]
        # Convert hours to DateTime
        inizio_m = hm2DT(day, day_table['inizio_m'])
        end_m = hm2DT(day, day_table['end_m'])
        inizio_p = hm2DT(day, day_table['inizio_p'])
        end_p = hm2DT(day, day_table['end_p'])
        # Get's the daily schedule
        day_start = inizio_m or inizio_p
        day_end = end_p or end_m
        return {'morning': BaseSlot(inizio_m, end_m),
                'afternoon': BaseSlot(inizio_p, end_p),
                'day': BaseSlot(day_start, day_end),
                }

    @property
    @memoize
    def weektable_boundaries(self):
        ''' Return the boundaries to draw the week table

        return a dict_like {'morning': slot1,
                            'afternoon': slot2}
        '''
        week_table = self.context.getSettimana_tipo()
        boundaries = {}
        for key in ('inizio_m', 'inizio_p'):
            boundaries[key] = min(day_table[key]
                                  for day_table in week_table
                                  if day_table[key])
        for key in ('end_m', 'end_p'):
            boundaries[key] = max(day_table[key]
                                  for day_table in week_table
                                  if day_table[key])
        for key, value in boundaries.iteritems():
            boundaries[key] = hm2seconds(value)
        return {'morning': BaseSlot(boundaries['inizio_m'],
                                    boundaries['end_m'],),
                'afternoon': BaseSlot(boundaries['inizio_p'],
                                      boundaries['end_p'],),
        }

    @memoize
    def get_bookings_in_day_folder(self, booking_date):
        '''
        The Prenotazione objects for today

        :param booking_date: a date as a datetime or a string
        '''
        day_folder = self.booker.get_container({'booking_date': booking_date})
        query = {'portal_type': self.booker.portal_type}
        bookings = day_folder.listFolderContents(query)
        bookings.sort(key=lambda x: x.getData_prenotazione())
        return bookings

    @memoize
    def get_slots_in_day_folder(self, booking_date):
        '''
        The Prenotazione objects for today

        :param booking_date: a date as a datetime or a string
        '''
        bookings = self.get_bookings_in_day_folder(booking_date)
        return map(ISlot, bookings)

    @memoize
    def get_slots_in_day_period(self, booking_date, period='day'):
        '''
        The Slots objects for today

        :param booking_date: a date as a datetime or a string
        :param period: a string
        '''
        interval = self.get_day_intervals(booking_date)[period]
        slots = self.get_slots_in_day_folder(booking_date)
        return [slot for slot in slots if slot in interval]

    @memoize
    def get_slots_in_day_period_by_gate(self, booking_date, period='day'):
        ''' This will return the busy slots divided by gate:

        return a dictionary like:
        {'gate1': [slot1],
         'gate2': [slot2, slot3],
        }
        '''
        slots_by_gate = {}
        slots = self.get_slots_in_day_period(booking_date, period)
        for slot in slots:
            slots_by_gate.setdefault(slot.gate, []).append(slot)
        return slots_by_gate

    @memoize
    def get_gates_availability_in_day_period(self, booking_date, period='day'):
        ''' Return the gates availability
        '''
        interval = self.get_day_intervals(booking_date)[period]
        slots_by_gate = self.get_slots_in_day_period_by_gate(booking_date,
                                                             period)
        gates = self.get_gates()
        availability = {}
        for gate in gates:
            gate_slots = slots_by_gate.get(gate, [])
            availability[gate] = interval - gate_slots
        return availability

    def get_tipology_duration(self, tipology):
        ''' Return the seconds for this tipology
        '''
        return int(tipology['duration']) * 60

    def get_first_slot(self, tipology, booking_date, period='day'):
        '''
        The Prenotazione objects for today

        :param tipology: a dict with name and duration
        :param booking_date: a date as a datetime or a string
        :param period: a DateTime object
        '''
        if booking_date < self.today:
            return
        availability = self.get_gates_availability_in_day_period(booking_date,
                                                                 period)
        good_slots = []
        duration = self.get_tipology_duration(tipology)

        hm_now = datetime.now().strftime('%H:%m')

        for slots in availability.itervalues():
            for slot in slots:
                if (len(slot) >= duration and
                    (booking_date > self.today
                     or slot.start() >= hm_now)):
                        good_slots.append(slot)
        if not good_slots:
            return
        good_slots.sort(key=lambda x: x.lower_value)
        return good_slots[0]

    def __call__(self):
        ''' Return itself
        '''
        return self
