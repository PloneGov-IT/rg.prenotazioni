# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime, timedelta
from five.formlib.formbase import PageForm
from plone.app.form.validators import null_validator
from plone.memoize.view import memoize
from quintagroup.formlib.captcha import Captcha, CaptchaWidget
from rg.prenotazioni import prenotazioniMessageFactory as _, tznow
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.adapters.conflict import IConflictManager
from urllib import urlencode
from zope.component._api import getUtility
from zope.formlib.form import FormFields, action
from zope.formlib.interfaces import WidgetInputError
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Choice, Datetime, TextLine, Text, ValidationError
from zope.schema.interfaces import IVocabularyFactory
import re


TELEPHONE_PATTERN = re.compile(r'^(\+){0,1}([0-9]| )*$')


class InvalidPhone(ValidationError):
    __doc__ = _('invalid_phone_number', u"Invalid phone number")


class InvalidEmailAddress(ValidationError):
    __doc__ = _('invalid_email_address', u"Invalid email address")


class IsNotfutureDate(ValidationError):
    __doc__ = _('is_not_future_date', u"This date is past")


def check_phone_number(value):
    '''
    If value exist it should match TELEPHONE_PATTERN
    '''
    if not value:
        return True
    if isinstance(value, basestring):
        value = value.strip()
    if TELEPHONE_PATTERN.match(value) is not None:
        return True
    raise InvalidPhone(value)


def check_valid_email(value):
    '''Check if value is a valid email address'''
    if not value:
        return True
    portal = getUtility(ISiteRoot)

    reg_tool = getToolByName(portal, 'portal_registration')
    if value and reg_tool.isValidEmail(value):
        return True
    else:
        raise InvalidEmailAddress


def check_is_future_date(value):
    '''
    Check if this date is in the future
    '''
    if not value:
        return True
    now = tznow()

    if isinstance(value, datetime) and value >= now:
        return True
    raise IsNotfutureDate


class IAddForm(Interface):
    """
    Interface for creating a prenotazione
    """
    booking_date = Datetime(
        title=_('label_booking_time', u'Booking time'),
        default=None,
        constraint=check_is_future_date,
    )
    fullname = TextLine(
        title=_('label_fullname', u'Fullname'),
        default=u'',
    )
    email = TextLine(
        title=_('label_email', u'Email'),
        required=True,
        default=u'',
        constraint=check_valid_email,
    )
    phone = TextLine(
        title=_('label_phone', u'Phone number'),
        required=False,
        default=u'',
        constraint=check_phone_number,
    )
    mobile = TextLine(
        title=_('label_mobile', u'Mobile number'),
        required=False,
        default=u'',
        constraint=check_phone_number,
    )
    tipology = Choice(
        title=_('label_tipology', u'Tipology'),
        required=True,
        default=u'',
        vocabulary='rg.prenotazioni.tipologies',
    )
    subject = Text(
        title=_('label_subject', u'Subject'),
        default=u'',
        required=False,
    )
    agency = TextLine(
        title=_('label_agency', u'Agency'),
        description=_('description_agency',
                      u'If you work for an agency please specify its name'),
        default=u'',
        required=False,
    )
    captcha = Captcha(
        title=_('label_captcha',
                u'Type the code from the picture shown below.'),
        default='',
    )


class AddForm(PageForm):
    """
    """
    implements(IAddForm)
    template = ViewPageTemplateFile('prenotazione_add.pt')

    hidden_fields = ["form.booking_date"]

    @property
    @memoize
    def is_anonymous(self):
        '''
        Check if user is anonymous
        '''
        return self.conte

    def len_tipologies(self):
        '''
        Check if we have tipologies defined here
        '''
        voc = getUtility(IVocabularyFactory, name="rg.prenotazioni.tipologies")
        return len(voc(self.context))

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(IAddForm)
        if not self.context.restrictedTraverse('plone_portal_state/anonymous')():
            ff = ff.omit('captcha')
        else:
            ff['captcha'].custom_widget = CaptchaWidget
        if not self.len_tipologies():
            ff = ff.omit('tipology')
        return ff

    def exceedes_date_limit(self, data):
        '''
        Check if we can book this slot or is it too much in the future.
        '''
        future_days = self.context.getFutureDays()
        if not future_days:
            return False
        booking_date = data.get('booking_date', None)
        if not isinstance(booking_date, datetime):
            return False
        date_limit = tznow() + timedelta(future_days)
        if booking_date <= date_limit:
            return False
        return True

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

    def validate(self, action, data):
        '''
        Checks if we can book those data
        '''
        errors = super(AddForm, self).validate(action, data)
        conflict_manager = IConflictManager(self.context.aq_inner)
        if conflict_manager.conflicts(data):
            msg = _(u'Sorry, this slot is not available anymore.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        if self.exceedes_date_limit(data):
            msg = _(u'Sorry, you can not book this slot for now.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        return errors

    def do_book(self, data):
        '''
        Create a Booking!
        '''
        booker = IBooker(self.context.aq_inner)
        return booker.create(data)

    @property
    @memoize
    def back_to_booking_url(self):
        ''' This goes back to booking view.
        '''
        try:
            b_date = self.request.get('form.booking_date', '')
            qs = urlencode({'data': DateTime(b_date).strftime('%d/%m/%Y')})
            return ('%s?%s') % (self.context.absolute_url(), qs)
        except:
            return self.context.absolute_url()

    @action(_('action_book', u'Book'), name=u'book')
    def action_book(self, action, data):
        '''
        Book this resource
        '''
        obj = self.do_book(data)
        msg = _('booking_created')
        IStatusMessage(self.request).add(msg, 'info')
        booking_date = data['booking_date'].strftime('%d/%m/%Y')
        qs = urlencode({'data': booking_date,
                        'uid': obj.UID()})
        target = ('%s/@@prenotazione_print?%s'
                  ) % (self.context.absolute_url(), qs)
        return self.request.response.redirect(target)

    @action(_(u"action_cancel", default=u"Cancel"),
            validator=null_validator, name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        target = self.back_to_booking_url
        return self.request.response.redirect(target)
