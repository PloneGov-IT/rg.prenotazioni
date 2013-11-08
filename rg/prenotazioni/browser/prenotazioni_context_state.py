# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser import BrowserView
from datetime import date, datetime
from plone import api
from plone.memoize.view import memoize
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.adapters.conflict import IConflictManager
from rg.prenotazioni.adapters.slot import ISlot, BaseSlot
from rg.prenotazioni import get_or_create_obj


def hm2handm(hm):
    ''' This is a utility function that will return the hour and date of day
    to the value passed in the string hm

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
    day_type = 'PrenotazioniDay'
    week_type = 'PrenotazioniWeek'
    year_type = 'PrenotazioniYear'

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

    @memoize
    def get_state(self, context):
        ''' Facade to the api get_state method
        '''
        if not context:
            return
        return api.content.get_state(context)

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
        return self.context.getGates() or ['']

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
                'stormynight': BaseSlot(0, 86400),
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

    def get_container(self, booking_date):
        ''' Return the container for bookings in this date
        '''
        if isinstance(booking_date, basestring):
            booking_date = DateTime(booking_date)
        year_id = booking_date.strftime('%Y')
        year = get_or_create_obj(self.context, year_id, self.year_type)
        week_id = booking_date.strftime('%W')
        week = get_or_create_obj(year, week_id, self.week_type)
        day_id = booking_date.strftime('%u')
        day = get_or_create_obj(week, day_id, self.day_type)
        return day

    @memoize
    def get_bookings_in_day_folder(self, booking_date):
        '''
        The Prenotazione objects for today, unfiltered but sorted by dates

        :param booking_date: a date as a datetime or a string
        '''
        day_folder = self.get_container(booking_date)
        allowed_portal_type = self.booker.portal_type
        bookings = [item[1] for item in day_folder.items()
                    if item[1].portal_type == allowed_portal_type]
        bookings.sort(key=lambda x: (x.getData_prenotazione(),
                                     x.getData_scadenza()))
        return bookings

    @memoize
    def get_existing_slots_in_day_folder(self, booking_date):
        '''
        The Prenotazione objects for today

        :param booking_date: a date as a datetime or a string
        '''
        bookings = self.get_bookings_in_day_folder(booking_date)
        return map(ISlot, bookings)

    @memoize
    def get_busy_slots_in_period(self, booking_date, period='day'):
        '''
        The busy slots objects for today: this filters the slots by review
        state

        :param booking_date: a datetime object
        :param period: a string
        :return: al list of slots
        [slot1, slot2, slot3]
        '''
        interval = self.get_day_intervals(booking_date)[period]
        if period == 'stormynight':
            allowed_review_states = ['refused']
        else:
            allowed_review_states = ['pending', 'published']
        # all slots
        slots = self.get_existing_slots_in_day_folder(booking_date)
        # the ones in the interval
        slots = [slot for slot in slots if slot in interval]
        # the one with the allowed review_state
        slots = [slot for slot in slots
                 if self.get_state(slot.context) in allowed_review_states]
        return sorted(slots)

    @memoize
    def get_busy_slots(self, booking_date, period='day'):
        ''' This will return the busy slots divided by gate:

        :param booking_date: a datetime object
        :param period: a string
        :return: a dictionary like:
        {'gate1': [slot1],
         'gate2': [slot2, slot3],
        }
        '''
        slots_by_gate = {}
        slots = self.get_busy_slots_in_period(booking_date, period)
        for slot in slots:
            slots_by_gate.setdefault(slot.gate, []).append(slot)
        return slots_by_gate

    @memoize
    def get_free_slots(self, booking_date, period='day'):
        ''' This will return the free slots divided by gate

        :param booking_date: a datetime object
        :param period: a string
        :return: a dictionary like:
        {'gate1': [slot1],
         'gate2': [slot2, slot3],
        }
        '''
        interval = self.get_day_intervals(booking_date)[period]
        slots_by_gate = self.get_busy_slots(booking_date, period)
        gates = self.get_gates()
        availability = {}
        for gate in gates:
            if interval:
                gate_slots = slots_by_gate.get(gate, [])
                availability[gate] = interval - gate_slots
            else:
                availability[gate] = []
        return availability

    def get_freebusy_slots(self, booking_date, period='day'):
        ''' This will return all the slots (free and busy) divided by gate

        :param booking_date: a datetime object
        :param period: a string
        :return: a dictionary like:
        {'gate1': [slot1],
         'gate2': [slot2, slot3],
        }
        '''
        free = self.get_free_slots(booking_date, period)
        busy = self.get_busy_slots(booking_date, period)
        keys = set(free.keys() + busy.keys())
        return {key: sorted(free.get(key, []) + busy.get(key, []))
                for key in keys}

    def get_tipology_duration(self, tipology):
        ''' Return the seconds for this tipology
        '''
        if isinstance(tipology, unicode):
            tipology = tipology.encode('utf8')
        if isinstance(tipology, dict):
            return int(tipology['duration']) * 60
        tipologie = self.context.getTipologia()
        for t in tipologie:
            if t['name'] == tipology:
                return int(t['duration'])
        return 1

    def get_first_slot(self, tipology, booking_date, period='day'):
        '''
        The Prenotazione objects for today

        :param tipology: a dict with name and duration
        :param booking_date: a date as a datetime or a string
        :param period: a DateTime object
        '''
        if booking_date < self.today:
            return
        availability = self.get_free_slots(booking_date,
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

    def get_less_used_gates(self, booking_date):
        '''
        Find which gate is les busy the day of the booking
        '''
        availability = self.get_free_slots(booking_date)
        # Create a dictionary where keys is the time the gate is free, and
        # value is a list of gates
        free_time_map = {}
        for gate, free_slots in availability.iteritems():
            free_time = sum(map(BaseSlot.__len__, free_slots))
            free_time_map.setdefault(free_time, []).append(gate)
        # Get a random choice among the less busy one
        max_free_time = max(free_time_map.keys())
        return free_time_map[max_free_time]

    def __call__(self):
        ''' Return itself
        '''
        return self
