# -*- coding: utf-8 -*-
from datetime import date
from five.formlib.formbase import PageForm
from plone.memoize.view import memoize
from rg.prenotazioni import (prenotazioniMessageFactory as _,
    prenotazioniLogger as logger)
from zope.formlib.form import FormFields, FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Choice, TextLine, ValidationError


class InvalidDate(ValidationError):
    __doc__ = _('invalid_date', u"Date should be in the format YYYY/mm/dd")


class InvalidTime(ValidationError):
    __doc__ = _('invalid_time', u"Date should be in the format HH:MM")


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


class IVacationBooker(Interface):
    gate = Choice(
        title=_('label_gate', u'Gate'),
        description=_('description_gate',
                      u'The gate that will be unavailable'),
        default=u'',
        vocabulary='rg.prenotazioni.gates',
    )
    start_date = TextLine(
        title=_('label_start_date', u'Start date'),
        constraint=check_date,
        default=u''
    )
    start_time = TextLine(
        title=_('label_start_time', u'Start time'),
        constraint=check_time,
        default=u'',
    )
    end_date = TextLine(
        title=_('label_end_date', u'End date'),
        constraint=check_date,
        default=u'',
    )
    end_time = TextLine(
        title=_('label_end_time', u'End time'),
        constraint=check_time,
        default=u''
    )


class VacationBooker(PageForm):
    '''
    This is a view that allows to book a gate for a certain period
    '''
    implements(IVacationBooker)

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(IVacationBooker)
        return ff

    def do_book(self, data):
        '''
        Execute the multiple booking
        '''
        return

    @action(_('action_book', u'Book'), name=u'book')
    def action_book(self, action, data):
        '''
        Book this resource
        '''
        obj = self.do_book(data)
        target = self.context.absolute_url()
        return self.request.response.redirect(target)

    @action(_('action_cancel', u'Cancel'), name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        target = self.context.absolute_url()
        return self.request.response.redirect(target)
