# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime, timedelta
from five.formlib.formbase import PageForm
from plone import api
from plone.app.form.validators import null_validator
from plone.memoize.view import memoize
from rg.prenotazioni import prenotazioniMessageFactory as _, tznow
from rg.prenotazioni.prenotazione_event import MovedPrenotazione
from rg.prenotazioni.utilities.urls import urlify
from zope.event import notify
from zope.formlib.form import FormFields, action
from zope.formlib.interfaces import WidgetInputError
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Datetime, TextLine


class IMoveForm(Interface):

    """
    Interface for moving a prenotazione
    """
    booking_date = Datetime(
        title=_('label_booking_time', u'Booking time'),
        default=None,
    )
    gate = TextLine(
        title=_('label_gate', u'Gate'),
        default=u'',
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

    @memoize
    def slot_styles(self, slot):
        '''
        Return a css to underline the moved slot
        '''
        context = slot.context
        if not context:
            return 'links'
        styles = [self.prenotazioni_view.get_state(context)]
        if context == self.context:
            styles.append("links")
        return " ".join(styles)

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
        # We inject the tipology of this context
        data['tipology'] = self.context.getTipologia_prenotazione()
        errors = super(MoveForm, self).validate(action, data)
        conflict_manager = self.prenotazioni_view.conflict_manager
        current_data = self.context.getData_prenotazione()
        current = {'booking_date': current_data.asdatetime(),
                   'tipology': data['tipology']}
        current_slot = conflict_manager.get_choosen_slot(current)
        current_gate = self.context.getGate()
        exclude = {current_gate: [current_slot]}

        if conflict_manager.conflicts(data, exclude=exclude):
            msg = _(u'Sorry, this slot is not available or does not fit your '
                    u'booking.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        if self.exceedes_date_limit(data):
            msg = _(u'Sorry, you can not book this slot for now.')
            self.set_invariant_error(errors, ['booking_date'], msg)
        for error in errors:
            api.portal.show_message(error.errors, self.request, type="error")
        return errors

    def do_move(self, data):
        '''
        Move a Booking!
        '''
        booking_date = DateTime(data['booking_date'])
        duration = self.context.getDuration()
        data_scadenza = booking_date + duration
        self.context.setData_prenotazione(booking_date)
        self.context.setData_scadenza(data_scadenza)
        self.context.setGate(data['gate'])
        notify(MovedPrenotazione(self.context))

    @property
    @memoize
    def back_to_booking_url(self):
        ''' This goes back to booking view.
        '''
        qs = {'data': (self.context.getData_prenotazione()
                       .strftime('%d/%m/%Y'))}
        return urlify(self.prenotazioni_folder.absolute_url(), params=qs)

    @memoize
    def move_to_slot_links(self, day, slot, gate):
        '''
        Returns the url to move the booking in this slot
        '''
        date = day.strftime("%Y-%m-%d")
        params = {'form.actions.move': 1,
                  'data': self.request.form.get('data', ''),
                  'form.gate': gate}
        times = slot.get_values_hr_every(300)
        urls = []
        base_url = "/".join((self.context.absolute_url(),
                             'prenotazione_move'))
        for t in times:
            params['form.booking_date'] = " ".join((date, t))
            urls.append({'title': t,
                         'url': urlify(base_url, params=params)})
        return urls

    @action(_('action_move', u'Move'), name=u'move')
    def action_move(self, action, data):
        '''
        Book this resource
        '''
        obj = self.do_move(data)
        obj  # pyflakes
        msg = _('booking_moved')
        IStatusMessage(self.request).add(msg, 'info')
        booking_date = data['booking_date'].strftime('%d/%m/%Y')
        target = urlify(self.prenotazioni_folder.absolute_url(),
                        paths=['prenotazioni_week_view'],
                        params={'data': booking_date})
        return self.request.response.redirect(target)

    @action(_(u"action_cancel", default=u"Cancel"),
            validator=null_validator, name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
        target = self.back_to_booking_url
        return self.request.response.redirect(target)

    def __call__(self):
        ''' Hide the portlets before serving the template
        '''
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        return super(MoveForm, self).__call__()
