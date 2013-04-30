# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from rg.prenotazioni import prenotazioniMessageFactory as _

class PrenotazioneView(BrowserView):
    """View for Prenotazione"""
    
    def __call__(self, *args, **kwargs):
        # trick for redirecting
        if self.request.get('HTTP_REFERER') and \
                '/portal_factory/Prenotazione/' in self.request.get('HTTP_REFERER'):
            putils = getToolByName(self.context, 'plone_utils')
            putils.addPortalMessage(_(u"Booking done"))
            self.request.response.redirect(self.context.aq_inner.aq_parent.absolute_url())
        return self.index()
