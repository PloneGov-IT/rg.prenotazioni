# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from rg.prenotazioni.config import MIN_IN_DAY
from urllib import urlencode


class PrenotazioneView(BrowserView):
    """View for Prenotazione"""

    @property
    @memoize
    def prenotazioni_folder(self):
        ''' The parent prenotazioni folder
        '''
        return self.context.getPrenotazioniFolder()

    @property
    @memoize
    def prenotazioni(self):
        ''' The context state of the parent prenotazioni folder
        '''
        return api.content.get_view('prenotazioni_context_state',
                                    self.prenotazioni_folder,
                                    self.request)

    @property
    def booking_date(self):
        ''' The parent prenotazioni folder
        '''
        return self.context.getData_prenotazione()

    @property
    @memoize
    def back_url(self):
        ''' Go back parent prenotazioni folder in the right day
        '''
        booking_date = self.booking_date
        target = self.prenotazioni_folder.absolute_url()
        if booking_date:
            qs = {'data': booking_date.strftime('%d/%m/%Y')}
            target = "%s?%s" % (target, urlencode(qs))
        return target


class ResetDuration(PrenotazioneView):
    ''' Reset data scadenza prenotazione: sometime is needed :p
    '''
    def reset_duration(self):
        ''' Reset the duration for this booking object
        '''
        tipology = self.context.getTipologia_prenotazione()
        duration = self.prenotazioni.get_tipology_duration(tipology)
        duration = (float(duration) / MIN_IN_DAY)
        self.context.setData_scadenza(self.booking_date + duration)

    def __call__(self):
        ''' Reset the dates
        '''
        self.reset_duration()
        return self.request.response.redirect(self.back_url)
