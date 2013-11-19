# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime, timedelta
from five.formlib.formbase import PageForm
from plone import api
from plone.app.form.validators import null_validator
from plone.memoize.view import memoize
from rg.prenotazioni import prenotazioniMessageFactory as _, tznow
from rg.prenotazioni.adapters.conflict import IConflictManager
from rg.prenotazioni.prenotazione_event import MovedPrenotazione
from urllib import urlencode
from zope.event import notify
from zope.formlib.form import FormFields, action
from zope.formlib.interfaces import WidgetInputError
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Datetime


class IMoveForm(Interface):

    """
    Interface for moving a prenotazione
    """
    booking_date = Datetime(
        title=_('label_booking_time', u'Booking time'),
        default=None,
    )


class MoveForm(PageForm):

    """ Controller for moving a booking
    """
    implements(IMoveForm)
    template = ViewPageTemplateFile('prenotazione_move.pt')

    hidden_fields = []

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        return FormFields(IMoveForm)

    @property
    @memoize
    def prenotazioni_folder(self):
        '''
        The PrenotazioniFolder object that contains the context
        '''
        return self.context.getPrenotazioniFolder()

    @property
    @memoize
    def prenotazioni_view(self):
        '''
        The prenotazioni_context_state view in the context
        of prenotazioni_folder
        '''
        return api.content.get_view('prenotazioni_context_state',
                                    self.prenotazioni_folder,
                                    self.request)

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
        errors = super(MoveForm, self).validate(action, data)
        conflict_manager = self.prenotazioni_view.conflict_manager
        if conflict_manager.conflicts(data):
            msg = _(u'Sorry, this slot is not available anymore.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        if self.exceedes_date_limit(data):
            msg = _(u'Sorry, you can not book this slot for now.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        return errors

    def do_move(self, data):
        '''
        Move a Booking!
        '''
        booking_date = data['booking_date']
        self.context.setData_prenotazione(booking_date)
        tipology = self.context.getTipologia_prenotazione()
        data_scadenza = self.prenotazioni_view.get_end_date(booking_date,
                                                            tipology)
        self.context.setData_scadenza(data_scadenza)
        notify(MovedPrenotazione(self.context))
        # self.context.reindexObject()

    @property
    @memoize
    def back_to_booking_url(self):
        ''' This goes back to booking view.
        '''
        qs = urlencode({'data': (self.context.getData_prenotazione()
                                 .strftime('%d/%m/%Y'))})
        return ('%s?%s') % (self.prenotazioni_folder.absolute_url(), qs)

    @action(_('action_move', u'Move'), name=u'move')
    def action_move(self, action, data):
        '''
        Book this resource
        '''
        obj = self.do_move(data)
        msg = _('booking_moved')
        IStatusMessage(self.request).add(msg, 'info')
        booking_date = data['booking_date'].strftime('%d/%m/%Y')
        qs = urlencode({'data': booking_date,
                        'uid': self.context.UID()})
        target = ('%s/@@prenotazione_print?%s'
                  ) % (self.prenotazioni_folder.absolute_url(), qs)
        return self.request.response.redirect(target)

    @action(_(u"action_cancel", default=u"Cancel"),
            validator=null_validator, name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        target = self.back_to_booking_url
        return self.request.response.redirect(target)
