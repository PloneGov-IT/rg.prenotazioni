# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize.view import memoize
from urllib import urlencode


class PrenotazionePrint(BrowserView):
    '''
    This is a view to proxy autorizzazione
    '''
    print_action = "javascript:this.print();"

    @property
    @memoize
    def prenotazione(self):
        '''
        Get's the prenotazione by uid
        '''
        uid = self.request.get("uid")
        if not uid:
            return
        pc = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'Prenotazione',
                 'UID': uid}
        brains = pc.unrestrictedSearchResults(query)
        if len(brains) != 1:
            return None

        return brains[0]._unrestrictedGetObject()

    def __call__(self):
        '''
        Se non c'e' la prenotazione vai all'oggetto padre
        '''
        if not self.prenotazione:
            qs = {}
            data = self.request.get('data')
            if data:
                qs['data'] = data
            msg = "Not found"
            IStatusMessage(self.request).add(msg, 'warning')
            target = '%s?%s' % (self.context.absolute_url(),
                                urlencode(qs))
            return self.request.response.redirect(target)
        else:
            return super(PrenotazionePrint, self).__call__()
