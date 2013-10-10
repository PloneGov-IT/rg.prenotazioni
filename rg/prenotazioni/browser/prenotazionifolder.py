# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from datetime import timedelta, date
from plone.memoize.view import memoize
from rg.prenotazioni import (prenotazioniMessageFactory as _,
                             prenotazioniLogger as logger, tznow)
from rg.prenotazioni.adapters.conflict import IConflictManager
from rg.prenotazioni.browser.base import BaseView
from rg.prenotazioni.prenotazione_event import MovedPrenotazione
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.event import notify
from rg.prenotazioni.browser import week

# TODO: Do not use the session anymore!


class PrenotazioniFolderView(week.View):

    """Default view of a PrenotazioniFolder
    """

    def getTime(self, day, slot, pm):
        """ restituisce l'ora associata allo slot indicato del giorno
        """
        durata = self.context.getDurata()
        minuti = timedelta(minutes=durata * slot,)
        inizio_m = day['inizio_m']
        inizio_p = day['inizio_p']

        if inizio_m != '0':
            inizio_m_minuti = int(inizio_m[2:4])
            inizio_m_ore = int(inizio_m[0:2])
            inizio_m_time = timedelta(hours=inizio_m_ore,
                                      minutes=inizio_m_minuti,)

        if inizio_p != '0':
            inizio_p_minuti = int(inizio_p[2:4])
            inizio_p_ore = int(inizio_p[0:2])
            inizio_p_time = timedelta(hours=inizio_p_ore,
                                      minutes=inizio_p_minuti,)

        if pm == 'm':
            new_timedelta = inizio_m_time + minuti
        elif pm == 'p':
            new_timedelta = inizio_p_time + minuti

        secondi = new_timedelta.seconds
        ore = secondi / 3600
        minuti = (secondi % 3600) / 60

        return str(ore).zfill(2) + ':' + str(minuti).zfill(2)

    def getPrenotazioni(self, day, orario):
        """restituisce le prenotazioni fissate per il giorno e l'ora indicati
        """
        pc = getToolByName(self.context, 'portal_catalog', None)
        giorno = DateTime(day.strftime('%Y/%m/%d') + ' ' + orario + ':00')
        prenotazioni = pc.unrestrictedSearchResults(
            portal_type='Prenotazione',
            Date=giorno,
            path='/'.join(self.context.getPhysicalPath()
                          )
        )
        return prenotazioni

    @memoize
    def getMinimumBookableDate(self):
        '''
        Return, if we have it, the maximum bookable date,
        i.e. today + the number of days specified in the container
        '''
        return date.today()

    @memoize
    def getMaximumBookableDate(self):
        '''
        Return, if we have it, the maximum bookable date,
        i.e. today + the number of days specified in the container
        '''
        future_days = self.context.getFutureDays()
        if not future_days:
            return None
        today = date.today()
        return today + timedelta(days=future_days)

    def displayPrenotazione(self, prenotazione, member):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name="plone_portal_state")
        if portal_state.anonymous():
            active_review_state = self.conflict_manager.active_review_state
            if prenotazione.review_state not in active_review_state:
                # Return target URL for the site anonymous visitors
                return False
        try:
            if prenotazione and member.has_permission(permissions.View,
                                                      prenotazione.getObject()):
                return True
        except Unauthorized:
            pass
        return False

    def canEditPrenotazione(self, prenotazione, member):
        try:
            if prenotazione and member.has_permission(
                permissions.ModifyPortalContent,
                    prenotazione.getObject()):
                return True
        except Unauthorized:
            pass
        return False

    def spanRow(self, day):
        """ restituisce lo span nel caso in cui ci sia orario continuato
        """
        if day['inizio_p'] != '0':
            return 1
        return 2

    @property
    @memoize
    def tznowstr(self):
        '''
        Return the tz aware now
        '''
        return tznow().strftime('%Y/%m/%d %H:%M:00')

    @property
    @memoize
    def date_limit(self):
        '''If it is not None, we cannot book for dates greater than this.
        '''
        future_days = self.context.getFutureDays()
        if not future_days:
            return
        return DateTime() + self.context.getFutureDays()

    def slots(self, day):
        """ restituisce gli slot disponibili nel giorno indicato
        """
        try:
            m = int(day['num_m'])
            p = int(day['num_p'])
        except:
            span = self.context.getDurata()
            mdiff = (int(day.get('end_m', '0'))
                     - int(day.get('inizio_m', '0')))
            pdiff = (int(day.get('end_p', '0'))
                     - int(day.get('inizio_p', '0')))
            m = mdiff / span
            p = pdiff / span
        return ([x for x in range(0, m)], [x for x in range(0, p)])

    def show_add_button(self, date_time):
        """ Show the plus button for the given date_time
        """
        if self.prenotazioni.uid_move_booking:
            return False
        if date_time < self.tznowstr:
            return False
        if self.date_limit:
            if DateTime(date_time) > self.date_limit:
                return False
        return self.conflict_manager.has_free_slots(date_time)


class MovePrenotazione(BaseView):

    """
    View to move a prenotazione (save data in session)
    """
    @property
    @memoize
    def conflict_manager(self):
        '''
        Return the conflict manager for this context
        '''
        return IConflictManager(self.context)

    def __call__(self, *args):
        uid = self.request.get('UID', '')
        self.request.SESSION.set('UID', uid)
        pu = getToolByName(self.context, 'plone_utils')
        pu.addPortalMessage(
            _(u"Seleziona la data nella quale spostare l'appuntamento"))
        self.request.RESPONSE.redirect(self.context.absolute_url())


class SavePrenotazione(BrowserView):

    """
    View to fix a prenotazione in another date
    """
    @property
    @memoize
    def conflict_manager(self):
        '''
        Return the conflict manager for this context
        '''
        return IConflictManager(self.context)

    def move(self):
        '''
        Move the prenotazione with the given UID
        '''
        uid = self.request.SESSION.get('UID', '')
        self.request.SESSION.set('UID', '')
        if not uid:
            msg = _('No UID')
            logger.debug(msg)
            return msg, 'info'

        try:
            date = DateTime(self.request.get('data_prenotazione', ''))
        except:
            msg = _('Problem with date')
            logger.exception(msg)
            return msg, 'error'

        if not self.conflict_manager.has_free_slots(date):
            msg = 'This slot is busy'
            logger.debug(msg)
            return msg, 'error'

        appuntamenti = self.conflict_manager.unrestricted_prenotazioni(UID=uid)
        if not appuntamenti:
            msg = 'No prenotazioni for %s in this context' % uid
            logger.debug(msg)
            return msg, 'error'

        appuntamento = appuntamenti[0]
        obj = appuntamento.getObject()
        obj.setData_prenotazione(date)
        obj.reindexObject()
        notify(MovedPrenotazione(obj))
        msg = _('Appuntamento spostato correttamente.')
        return msg, 'info'

    def __call__(self, *args):
        msg, msg_type = self.move()
        pu = getToolByName(self.context, 'plone_utils')
        pu.addPortalMessage(msg, msg_type)
        self.request.RESPONSE.redirect(self.context.absolute_url())


class CancelSpostamento(BrowserView):

    """
    View to cancel the prenotazione move (deletes data in session)
    """

    def __call__(self, *args):
        self.request.SESSION.set('UID', '')
        self.request.RESPONSE.redirect(self.context.absolute_url())
