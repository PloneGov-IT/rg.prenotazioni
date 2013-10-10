# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
from rg.prenotazioni.adapters.conflict import IConflictManager


class BaseView(BrowserView):

    ''' base view for rg.prenotazioni

    Give some handy cached methods
    '''
    @property
    @memoize
    def prenotazioni(self):
        ''' Returns the prenotazioni_context_state view.

        Everyone should know about this!
        '''
        return self.context.restrictedTraverse('@@prenotazioni_context_state')

    @property
    @memoize
    def conflict_manager(self):
        '''
        Return the conflict manager for this context
        '''
        return IConflictManager(self.context)
