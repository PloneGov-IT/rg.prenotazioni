# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from five.formlib.formbase import PageForm
from plone.memoize.view import memoize
from quintagroup.formlib.captcha import Captcha, CaptchaWidget
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.adapters.conflict import IConflictManager
from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Datetime, TextLine, Text


class IAddForm(Interface):
    """
    Interface for creating a prenotazione
    """
    fullname = TextLine(
        title=_('label_fullname', u'Fullname'),
        default=u'',
    )
    subject = Text(
        title=_('label_subject', u'Subject'),
        default=u'',
        required=False,
    )
    booking_date = Datetime(
        title=_('label_booking_time', u'Booking time'),
        default=None,
    )
    agency = TextLine(
        title=_('label_agency', u'Agency'),
        description=_('description_agency',
                      u'If you work for an agency please specify its name'),
        default=u'',
        required=False,
    )
    phone = TextLine(
        title=_('label_phone', u'Phone number'),
        required=False,
        default=u'',
    )
    email = TextLine(
        title=_('label_email', u'Email'),
        default=u'',
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

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(IAddForm)
        ff['captcha'].custom_widget = CaptchaWidget
        return ff

    def booking_validator(self, action, data):
        '''
        Checks if we can book those data
        '''
        errors = super(AddForm, self).validate(action, data)
        conflict_manager = IConflictManager(self.context.aq_inner)
        if conflict_manager.conflicts(data):
            errors.append
        return errors

    def do_book(self, data):
        '''
        Create a Booking!
        '''
        booker = IBooker(self.context.aq_inner)
        return booker.create(data)

    @action(_('action_book', u'Book'), name=u'book',
            validator="booking_validator")
    def action_book(self, action, data):
        '''
        Book this resource
        '''
        self.do_book(data)
        msg = _('booking_created', 'Booking created')
        IStatusMessage(self.request).add(msg, 'info')
        booking_date = data['booking_date'].strftime('%d/%m/%Y')
        target = ('%s?data=%s') % (self.context.absolute_url(), booking_date)
        self.request.response.redirect(target)

    @action(_('action_cancel', u'Cancell'), name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        return
