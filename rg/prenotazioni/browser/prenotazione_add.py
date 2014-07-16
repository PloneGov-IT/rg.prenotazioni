# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime, timedelta
from five.formlib.formbase import PageForm
from plone import api
from plone.app.form.validators import null_validator
from plone.memoize.view import memoize
from quintagroup.formlib.captcha import Captcha, CaptchaWidget
from rg.prenotazioni import prenotazioniMessageFactory as _, tznow, TZ
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.utilities.urls import urlify
from zope.app.form.browser import RadioWidget
from zope.component._api import getUtility
from zope.formlib.form import FormFields, action
from zope.formlib.interfaces import WidgetInputError
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Choice, Datetime, TextLine, Text, ValidationError
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
    tipology = Choice(
        title=_('label_tipology', u'Tipology'),
        required=True,
        default=u'',
        vocabulary='rg.prenotazioni.tipologies',
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


def TipologyWidget(field, request):
    ''' Custom radio widget
    '''
    class TipologyRadioWidget(RadioWidget):
        ''' Override tipology RadioWidget
        '''
        template = ViewPageTemplateFile('tipology_radio_widget.pt')

        @property
        @memoize
        def prenotazione_add(self):
            ''' Returns the prenotazioni_context_state view.

            Everyone should know about this!
            '''
            return api.content.get_view('prenotazione_add',
                                        self.context.context.aq_inner,
                                        self.request)

        @property
        @memoize
        def tipologies_bookability(self):
            ''' Get tipology bookability
            '''
            booking_date = self.prenotazione_add.booking_DateTime.asdatetime()
            prenotazioni = self.prenotazione_add.prenotazioni
            return prenotazioni.tipologies_bookability(booking_date)

        @property
        @memoize
        def items(self):
            ''' Get tipology bookability
            '''
            voc = self.context.vocabulary
            return [term for term in voc]

        @property
        @memoize
        def bookable_items(self):
            ''' Get tipology bookability
            '''
            keys = sorted(self.tipologies_bookability['bookable'])
            keys = [key.decode('utf8') for key in keys]
            voc = self.context.vocabulary
            return [voc.getTerm(key) for key in keys if key in voc]

        @property
        @memoize
        def unbookable_items(self):
            ''' Get tipology bookability
            '''
            keys = sorted(self.tipologies_bookability['unbookable'])
            keys = [key.decode('utf8') for key in keys]
            voc = self.context.vocabulary
            return [voc.getTerm(key) for key in keys if key in voc]

        def __call__(self):
            """ Call our beautiful template
            """
            return self.template()

    return TipologyRadioWidget(field, field.vocabulary, request)


class AddForm(PageForm):
    """
    """
    implements(IAddForm)
    template = ViewPageTemplateFile('prenotazione_add.pt')

    hidden_fields = ["form.booking_date"]
    render_form = False

    @property
    @memoize
    def localized_time(self):
        ''' Facade for context/@@plone/toLocalizedTime
        '''
        return api.content.get_view('plone',
                                    self.context,
                                    self.request).toLocalizedTime

    @property
    @memoize
    def label(self):
        '''
        Check if user is anonymous
        '''
        booking_date = self.booking_DateTime
        if not booking_date:
            return ''
        localized_date = self.localized_time(booking_date)
        return _('label_selected_date',
                 u"Selected date: ${date} — Time slot: ${slot}",
                 mapping={'date': localized_date,
                          'slot': booking_date.hour()})

    @property
    @memoize
    def description(self):
        '''
        Check if user is anonymous
        '''
        return _('help_prenotazione_add', u"")

    @property
    @memoize
    def booking_DateTime(self):
        ''' Return the booking_date as passed in the request as a DateTime
        object
        '''
        booking_date = self.request.form.get('form.booking_date', None)
        if not booking_date:
            return None
        if len(booking_date) == 16:
            booking_date = ' '.join((booking_date, TZ._tzname))
        return DateTime(booking_date)

    @property
    @memoize
    def is_anonymous(self):
        '''
        Check if user is anonymous
        '''
        return api.content.get_view('plone_portal_state',
                                    self.context,
                                    self.request).anonymous()

    @property
    @memoize
    def prenotazioni(self):
        ''' Returns the prenotazioni_context_state view.

        Everyone should know about this!
        '''
        return api.content.get_view('prenotazioni_context_state',
                                    self.context,
                                    self.request)

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(IAddForm)
        if not self.is_anonymous:
            ff = ff.omit('captcha')
        else:
            ff['captcha'].custom_widget = CaptchaWidget
        ff['tipology'].custom_widget = TipologyWidget
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
        if not data.get('booking_date'):
            return errors
        conflict_manager = self.prenotazioni.conflict_manager
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
        params = self.prenotazioni.remembered_params.copy()
        b_date = self.booking_DateTime
        if b_date:
            params['data'] = b_date.strftime('%d/%m/%Y')
        target = urlify(self.context.absolute_url(), params=params)
        return target

    @action(_('action_book', u'Book'), name=u'book')
    def action_book(self, action, data):
        '''
        Book this resource
        '''
        obj = self.do_book(data)
        msg = _('booking_created')
        IStatusMessage(self.request).add(msg, 'info')
        booking_date = data['booking_date'].strftime('%d/%m/%Y')
        params = {'data': booking_date,
                  'uid': obj.UID()}
        target = urlify(self.context.absolute_url(),
                        paths=["@@prenotazione_print"],
                        params=params)
        return self.request.response.redirect(target)

    @action(_(u"action_cancel", default=u"Cancel"),
            validator=null_validator, name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        target = self.back_to_booking_url
        return self.request.response.redirect(target)

    def show_message(self, msg, msg_type):
        ''' Facade for the show message api function
        '''
        show_message = api.portal.show_message
        return show_message(msg, request=self.request, type=msg_type)

    def redirect(self, target, msg="", msg_type="error"):
        """ Redirects the user to the target, optionally with a portal message
        """
        if msg:
            self.show_message(msg, msg_type)
        return self.request.response.redirect(target)

    def has_enough_time(self):
        """ Check if we have enough time to book something
        """
        booking_date = self.booking_DateTime.asdatetime()
        return self.prenotazioni.is_booking_date_bookable(booking_date)

    def __call__(self):
        ''' Redirects to the context if no data is found in the request
        '''
        # we should always have a booking date
        if not self.booking_DateTime:
            msg = _('please_pick_a_date', "Please select a time slot")
            return self.redirect(self.back_to_booking_url, msg)
        # and if we have it, we should have enough time to do something
        if not self.has_enough_time():
            msg = _('time_slot_to_short',
                    "You cannot book any typology at this time")
            return self.redirect(self.back_to_booking_url, msg)
        return super(AddForm, self).__call__()
