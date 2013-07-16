# -*- coding: utf-8 -*-
from datetime import date
from five.formlib.formbase import PageForm
from plone.memoize.view import memoize
from rg.prenotazioni import (prenotazioniMessageFactory as _,
    prenotazioniLogger as logger, time2timedelta)
from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Choice, TextLine, ValidationError
from Products.Five.browser import BrowserView
from DateTime import DateTime
from rg.prenotazioni.adapters.booker import IBooker
from Products.statusmessages.interfaces import IStatusMessage
from zope.formlib.interfaces import WidgetInputError
from rg.prenotazioni.adapters.conflict import IConflictManager


class InvalidDate(ValidationError):
    __doc__ = _('invalid_date')


class InvalidTime(ValidationError):
    __doc__ = _('invalid_time')


def check_date(value):
    '''
    If value exist it should match TELEPHONE_PATTERN
    '''
    if not value:
        return True
    if isinstance(value, basestring):
        value = value.strip()
    try:
        date(*map(int, value.split('/')))
        return True
    except:
        msg = 'Invalid date: %r' % value
        logger.exception(msg)
    raise InvalidDate(value)


def check_time(value):
    '''
    If value exist it should match TELEPHONE_PATTERN
    '''
    if not value:
        return True
    if isinstance(value, basestring):
        value = value.strip()
    try:
        hh, mm = map(int, value.split(':'))
        assert 0 <= hh <= 23
        assert 0 <= mm <= 59
        return True
    except:
        msg = 'Invalid time: %r' % value
        logger.exception(msg)
    raise InvalidTime(value)


class IVacationBooking(Interface):
    title = TextLine(
        title=_('label_title', u'Title'),
        description=_('description_title',
                      u'This text will appear in the calendar cells'),
        default=u'',
    )
    gate = Choice(
        title=_('label_gate', u'Gate'),
        description=_('description_gate',
                      u'The gate that will be unavailable'),
        default=u'',
        vocabulary='rg.prenotazioni.gates',
    )
    start_date = TextLine(
        title=_('label_start_date', u'Start date'),
        description=_('invalid_date'),
        constraint=check_date,
        default=u''
    )
    start_time = TextLine(
        title=_('label_start_time', u'Start time'),
        description=_('invalid_time'),
        constraint=check_time,
        default=u'00:00',
    )
    end_time = TextLine(
        title=_('label_end_time', u'End time'),
        description=_('invalid_time'),
        constraint=check_time,
        default=u'23:59'
    )


class VacationBooking(PageForm):
    '''
    This is a view that allows to book a gate for a certain period
    '''
    implements(IVacationBooking)

    def get_parsed_data(self, data):
        '''
        Return the data already parsed for our convenience
        '''
        parsed_data = data.copy()
        parsed_data['start_date'] = DateTime(data['start_date'])
        parsed_data['start_time'] = time2timedelta(data['start_time'])
        parsed_data['end_time'] = time2timedelta(data['end_time'])
        return parsed_data

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(IVacationBooking)
        today = unicode(date.today().strftime('%Y/%m/%d'))
        ff['start_date'].field.default = today
        if not self.context.getGates():
            ff = ff.omit('gate')
        return ff

    def get_slots(self, data):
        '''
        Get the slots we want to book!
        '''
        start_date = data['start_date']
        start_time = start_date.asdatetime() + data['start_time']
        end_time = start_date.asdatetime() + data['end_time']

        pcs = self.context.restrictedTraverse('@@prenotazioni_context_state')
        slots = pcs.get_slots_in_day(start_date)
        slots = slots['p'] + slots['m']
        slots = [slot for slot in slots if start_time < slot < end_time]
        return slots

    def do_book(self, data):
        '''
        Execute the multiple booking
        '''
        booker = IBooker(self.context.aq_inner)
        slots = self.get_slots(data)

        for slot in slots:
            slot_data = {'fullname': data['title'],
                         'subject': u'',
                         'agency': u'',
                         'booking_date': slot,
                         'telefono': u'',
                         'mobile': u'',
                         'email': u'',
                         'tipologia_prenotazione': u'',
                         }
            booker.create(slot_data, force_gate=data.get('gate'))

        msg = _('booking_created')
        IStatusMessage(self.request).add(msg, 'info')

    def set_invariant_error(self, errors, fields, msg):
        '''
        Set an error with invariant validation to highlights the involved
        fields
        '''
        for field in fields:
            label = self.widgets[field].label
            error = WidgetInputError(field, label, msg)
            errors.append(error)
            self.widgets[field].error = msg

    def has_slot_conflicts(self, data):
        ''' We want the operator to handle conflicts
        '''
        conflict_manager = IConflictManager(self.context.aq_inner)
        slots = self.get_slots(data)
        query = {'Date': [DateTime(slot) for slot in slots],
                 'review_state': conflict_manager.active_review_state}
        brains = conflict_manager.unrestricted_prenotazioni(**query)
        for brain in brains:
            obj = brain.getObject()
            if obj.getGate() == data['gate']:
                return True

    def validate(self, action, data):
        '''
        Checks if we can book those data
        '''
        errors = super(VacationBooking, self).validate(action, data)
        parsed_data = self.get_parsed_data(data)
        if self.has_slot_conflicts(parsed_data):
            msg = _('slot_conflict_error',
                    u'This gate has some booking schedule in this time '
                    u'period.')
            fields_to_notify = ['start_date', 'start_time', 'end_time']
            self.set_invariant_error(errors, fields_to_notify, msg)
        return errors

    @action(_('action_book', u'Book'), name=u'book')
    def action_book(self, action, data):
        '''
        Book this resource
        '''
        parsed_data = self.get_parsed_data(data)
        self.do_book(parsed_data)

    @action(_('action_cancel', u'Cancel'), name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        target = self.context.absolute_url()
        return self.request.response.redirect(target)


class VacationBookingShow(BrowserView):
    '''
    Should this functionality be published?
    '''
    def __call__(self):
        ''' Return True for the time being
        '''
        return True
