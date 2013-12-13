# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
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
