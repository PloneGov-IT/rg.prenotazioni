# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from five.formlib.formbase import PageForm
from plone.memoize.view import memoize
from quintagroup.formlib.captcha import Captcha, CaptchaWidget
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.adapters.booker import IBooker
from rg.prenotazioni.adapters.conflict import IConflictManager
from urllib import urlencode
from zope.component._api import getUtility
from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Choice, Datetime, TextLine, Text
from zope.schema.interfaces import IVocabularyFactory
from zope.formlib.interfaces import WidgetInputError


class IAddForm(Interface):
    """
    Interface for creating a prenotazione
    """
    fullname = TextLine(
        title=_('label_fullname', u'Fullname'),
        default=u'',
    )
    email = TextLine(
        title=_('label_email', u'Email'),
        default=u'',
    )
    phone = TextLine(
        title=_('label_phone', u'Phone number'),
        required=False,
        default=u'',
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
            msg = _(u'Sorry this slot is not available anymore.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        return errors

    def do_book(self, data):
        '''
        Create a Booking!
        '''
        booker = IBooker(self.context.aq_inner)
        return booker.create(data)

    @action(_('action_book', u'Book'), name=u'book')
    def action_book(self, action, data):
        '''
        Book this resource
        '''
        obj = self.do_book(data)
        msg = _('booking_created', 'Booking created')
        IStatusMessage(self.request).add(msg, 'info')
        booking_date = data['booking_date'].strftime('%d/%m/%Y')
        qs = urlencode({'data': booking_date,
                        'uid': obj.UID()})
        target = ('%s/@@prenotazione_print?%s'
                  ) % (self.context.absolute_url(), qs)
        self.request.response.redirect(target)

    @action(_('action_cancel', u'Cancell'), name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        return
